import numpy as np
import pandas as pd
import streamlit as st
from streamlit_tags import st_tags
from datetime import datetime


def _calculate_interest_rate(margin, wibor):
    return margin + wibor

def _calculate_installement(payments_number, credit_principal, interest_rate):
    return credit_principal*(((1+(interest_rate/12))**payments_number)*interest_rate/12)/(((1+(interest_rate/12))**payments_number)-1)

def _calculate_interest(credit_principle, interest_rate):
    return credit_principle * interest_rate / 12

def _calculate_principle(installment, interest):
    return installment - interest

def _calculate_perc(principle, installment):
    return principle / installment * 100

@st.cache_data
def calc_credit(settings, add_principle_list, change_wibor_list, short_term_list, vacations_list):

    payments_number = settings['payments_number'] + len(vacations_list)

    data = np.zeros((payments_number)
    , dtype=[
        ('payments_number', 'f8'),
        ('date', 'datetime64[M]'),
        ('credit_principle', 'f8'),
        ('add_principle', 'f8'),
        ('margin', 'f8'),
        ('wibor', 'f8'),
        ('interest_rate', 'f8'),
        ('installment', 'f8'),
        ('interest', 'f8'),
        ('principle', 'f8'),
        ('perc', 'f8'),
        ('interest_sum', 'f8'),
    ])

    # fill initial values
    data[0]['payments_number'] = payments_number
    data[0]['date'] = settings['start_date']
    data[0]['credit_principle'] = settings['credit_principle']
    data[0]['add_principle'] = 0
    data[0]['margin'] = settings['margin']
    data[0]['wibor'] = settings['wibor']
    data[0]['interest_rate'] = _calculate_interest_rate(data[0]['margin'], data[0]['wibor'])
    data[0]['installment'] = _calculate_installement(data[0]['payments_number'], data[0]['credit_principle'], data[0]['interest_rate'])
    data[0]['interest'] = _calculate_interest(data[0]['credit_principle'], data[0]['interest_rate'])
    data[0]['principle'] = _calculate_principle(data[0]['installment'], data[0]['interest'])
    data[0]['perc'] = _calculate_perc(data[0]['principle'], data[0]['installment'])
    data[0]['interest_sum'] = data[0]['interest']

    for i in range(1, data.shape[0]):
        
        data[i]['date'] = data[i-1]['date'] + np.timedelta64(1, 'M')

        data[i]['payments_number'] = data[i-1]['payments_number'] - 1
        for short_term in short_term_list:
            if np.datetime64(short_term[0]) == data[i]['date']:
                data[i]['payments_number'] = data[i]['payments_number'] - float(short_term[1])

        data[i]['credit_principle'] = data[i-1]['credit_principle'] - data[i-1]['principle']
        for add_principle in add_principle_list:
            if np.datetime64(add_principle[0]) == data[i]['date']:
                data[i]['add_principle'] = float(add_principle[1])
                if data[i]['credit_principle'] - float(add_principle[1]) > 0:
                    data[i]['credit_principle'] = data[i]['credit_principle'] - data[i]['add_principle']
                else:
                    data[i]['add_principle'] = data[i]['credit_principle']
                    data[i]['credit_principle'] = 0

        data[i]['wibor'] = data[i-1]['wibor']
        for change_wibor in change_wibor_list:
            if np.datetime64(change_wibor[0]) == data[i]['date']:
                data[i]['wibor'] = data[i]['wibor'] + float(change_wibor[1])

        found = False
        for vacations in vacations_list:
            if np.datetime64(vacations[0]) == data[i]['date']:
                found = True
        if found:
            data[i]['margin'] = data[i-1]['margin']
            data[i]['interest_rate'] = 0
            data[i]['installment'] = data[i-1]['installment']
            data[i]['interest'] = 0
            data[i]['principle'] = 0
            data[i]['perc'] = data[i-1]['perc']
            data[i]['interest_sum'] = data[i-1]['interest_sum'] + data[i]['interest']
        else:
            data[i]['margin'] = data[i-1]['margin']
            data[i]['interest_rate'] = _calculate_interest_rate(data[i]['margin'], data[i]['wibor'])
            data[i]['installment'] = _calculate_installement(data[i]['payments_number'], data[i]['credit_principle'], data[i]['interest_rate'])
            data[i]['interest'] = _calculate_interest(data[i]['credit_principle'], data[i]['interest_rate'])
            data[i]['principle'] = _calculate_principle(data[i]['installment'], data[i]['interest'])
            if data[i]['credit_principle'] == 0 and data[i]['add_principle'] != 0:
                data[i]['perc'] = 0
            else:
                data[i]['perc'] = _calculate_perc(data[i]['principle'], data[i]['installment'])
            data[i]['interest_sum'] = data[i-1]['interest_sum'] + data[i]['interest']

        # Savings
        if data[i]['payments_number'] <= 0:
            data[i]['installment'] = 0

    data = data[data['payments_number'] > 0]

    return data

def language_dict(language):
    if language == 'English':
        return {
            'version': 'Version',
            'title': 'Debt Payment Calculator',
            'settings': 'Settings',
            'credit_principle': 'Credit Principle Amount',
            'margin': 'Fixed Rate (%)',
            'wibor': 'Adjustable Rate (%)',
            'payments_number': 'Number of Payments (months)',
            'start_date': 'Start Date',
            'add_principle': 'Lump Sum Payment',
            'change_wibor': 'Change Adjustable Rate',
            'short_term': 'Short Loan Term',
            'vacations': 'Adjust Payment Holidays',
            'add_principle_text': 'Add additional principle payment. 2025-08,20000',
            'change_wibor_text': 'Change adjustment rate. 2025-08,-0.0025',
            'short_term_text': 'Short term of loan. 2025-08,72',
            'vacations_text': 'Add payments holiday. 2025-08,0',
            'total_interest': 'Total Interest',
            'payoff_date': 'Payoff Date',
            'sum_additional_payments': 'Sum of Additional Payments',
            'perc_additional_payments': 'Percent of Additional Payments',
            'summary_table': 'See summary table',
            'summary_table_nothing': 'See summary table for no additional payments or short term',
            'show_prec_principle': 'Show % of principle in installment',
            'disclaimer': """
                **Disclaimer for Debt Calculator**\n
                This debt calculator (the "Tool") is provided for informational and educational purposes only. The calculations and results generated by this Tool are estimates based solely on the information you input and are intended for general illustration only.\n
                **Not Financial, Legal, or Tax Advice:**\n
                The information and calculations provided by this Tool do not constitute, and should not be considered as, financial, legal, tax, or investment advice.\n
                **Hypothetical and Estimates Only:**\n
                The results presented are hypothetical and may not reflect your actual financial situation, loan terms, or future outcomes. Your personal financial situation is unique, and factors outside of this Tool's scope, such as changes in interest rates, fees, or your individual circumstances, can significantly impact actual results.\n
                **Consult a Professional:**\n
                Before making any financial decisions or taking any action based on the information provided by this Tool, you should always seek independent, professional financial advice from a qualified financial advisor, legal counsel, or tax professional who can assess your specific situation and needs.\n
                **User Responsibility:**\n
                Your use of this Tool is entirely at your own risk. You acknowledge and agree that you are solely responsible for any decisions or actions taken in reliance upon or as a result of the information provided by this Tool. We disclaim all liability and responsibility for any loss of any kind whatsoever, which may result from the use of, or reliance on, the estimates or information provided by this Tool.\n
            """,

        }
    elif language == 'Polski':
        return {
            'version': 'Wersja',
            'title': 'Kalkulator Wczaśniejszej Spłaty Kredytu',
            'settings': 'Ustawienia',
            'credit_principle': 'Kwota kredytu',
            'margin': 'Marża (%)',
            'wibor': 'WIBOR/POLSTR (%)',
            'payments_number': 'Liczba rat (miesiące)',
            'start_date': 'Data rozpoczęcia',
            'add_principle': 'Nadpłata kapitału',
            'change_wibor': 'Zmiana WIBOR/POLSTR',
            'short_term': 'Skrócenie okresu kredytowania',
            'vacations': 'Wakacje kredytowe',
            'add_principle_text': 'Dodaj nadpłatę kredytu. 2025-08,20000',
            'change_wibor_text': 'Dodaj zmianę WIBOR/POLSTR. 2025-08,-0.0025',
            'short_term_text': 'Skróć okres kredytowania. 2025-08,72',
            'vacations_text': 'Dodaj wakacje kredytowe. 2025-08,0',
            'total_interest': 'Suma Odsetek',
            'payoff_date': 'Data Spłaty Kredytu',
            'sum_additional_payments': 'Suma Nadpłat Kredytu',
            'perc_additional_payments': 'Procent Nadpłat Kredytu',
            'summary_table': 'Tabela z podsumowaniem',
            'summary_table_nothing': 'Tabela z podsumowaniem bez dodatkowych nadpłat i skrócenia okresu',
            'show_prec_principle': 'Pokaż % kapitału w racie',
            'disclaimer': """
                **Zastrzeżenie dotyczące Kalkulatora Wczaśniejszej Spłaty Kredytu**\n
                Niniejszy kalkulator wcześniejszej spłaty kredytu („Narzędzie”) jest udostępniany wyłącznie w celach informacyjnych i edukacyjnych. Obliczenia i wyniki generowane przez to Narzędzie są szacunkami opartymi wyłącznie na wprowadzonych przez Ciebie danych i służą jedynie do ogólnego zobrazowania.\n
                **Nie stanowi porady finansowej, prawnej ani podatkowej:**\n
                Informacje i obliczenia dostarczone przez to Narzędzie nie stanowią i nie powinny być traktowane jako porada finansowa, prawna, podatkowa ani inwestycyjna.\n
                **Wyłącznie hipotezy i szacunki:**\n
                Przedstawione wyniki mają charakter hipotetyczny i mogą nie odzwierciedlać Twojej rzeczywistej sytuacji finansowej, warunków pożyczki lub kredytu ani przyszłych rezultatów. Twoja osobista sytuacja finansowa jest wyjątkowa, a czynniki spoza zakresu tego Narzędzia, takie jak zmiany stóp procentowych, opłat lub Twoich indywidualnych okoliczności, mogą znacząco wpłynąć na rzeczywiste wyniki.\n
                **Skonsultuj się z profesjonalistą:**\n
                Przed podjęciem jakichkolwiek decyzji finansowych lub działań w oparciu o informacje dostarczone przez to Narzędzie, zawsze powinieneś zasięgnąć niezależnej, profesjonalnej porady finansowej u wykwalifikowanego doradcy finansowego, radcy prawnego lub doradcy podatkowego, który może ocenić Twoją konkretną sytuację i potrzeby.\n
                **Odpowiedzialność użytkownika:**\n
                Korzystanie z tego Narzędzia odbywa się wyłącznie na własne ryzyko. Potwierdzasz i zgadzasz się, że ponosisz wyłączną odpowiedzialność za wszelkie decyzje lub działania podjęte w oparciu o informacje dostarczone przez to Narzędzie lub w ich wyniku. Zrzekamy się wszelkiej odpowiedzialności za wszelkie straty jakiegokolwiek rodzaju, które mogą wyniknąć z użytkowania lub polegania na szacunkach lub informacjach dostarczonych przez to Narzędzie.\n
            """,
        }
    else:
        return {}

if __name__ == "__main__":

    version = '1.0.0'

    with st.sidebar:
        lang_list = ['English', 'Polski']
        language = st.pills('', lang_list, selection_mode='single', default=lang_list[0], label_visibility="collapsed")
        language = language_dict(language)
        st.header(language['settings'])
        st.write(f"{language['version']}: {version}")
        st.write('---')
        st.session_state['credit_principle'] = st.number_input(language['credit_principle'], min_value=1000, value=185000, step=1000)
        st.session_state['margin'] = st.number_input(language['margin'], min_value=0.0, value=1.75, step=0.01)
        st.session_state['wibor'] = st.number_input(language['wibor'], min_value=0.0, value=1.79, step=0.01)
        st.session_state['payments_number'] = st.number_input(language['payments_number'], min_value=1, value=300, step=1)
        st.session_state['start_date'] = st.date_input(language['start_date'], value=datetime(2020, 3, 1))
        st.session_state['vacations_toggle'] = st.checkbox(language['vacations'], value=False)
        st.session_state['perc_toggle'] = st.checkbox(language['show_prec_principle'], value=False)
    
    st.title(language['title'])

    st.session_state['settings'] = {
        'credit_principle': st.session_state['credit_principle'],
        'margin': st.session_state['margin'] / 100,
        'wibor': st.session_state['wibor'] / 100,
        'payments_number': st.session_state['payments_number'],
        'start_date': np.datetime64(st.session_state['start_date']),
    }

    value_tmp = []

    st.session_state['add_principle_list'] = st_tags(label='', text=language['add_principle_text'], value=value_tmp, suggestions=[], maxtags = 100)
    
    st.session_state['change_wibor_list'] = st_tags(label='', text=language['change_wibor_text'], value=value_tmp, suggestions=[], maxtags = 100)
    
    st.session_state['short_term_list'] = st_tags(label='', text=language['short_term_text'], value=value_tmp, suggestions=[], maxtags = 100)
    
    if st.session_state['vacations_toggle']:
        st.session_state['vacations_list'] = st_tags(label='', text=language['vacations_text'], value=value_tmp, suggestions=[], maxtags = 100)
    else:
        st.session_state['vacations_list'] = []

    add_principle_list = []
    if len(st.session_state['add_principle_list']) != 0:
        add_principle_list = [add.split(',') for add in st.session_state['add_principle_list']]

    change_wibor_list = []
    if len(st.session_state['change_wibor_list']) != 0:
        change_wibor_list = [add.split(',') for add in st.session_state['change_wibor_list']]

    short_term_list = []
    if len(st.session_state['short_term_list']) != 0:
        short_term_list = [add.split(',') for add in st.session_state['short_term_list']]

    vacations_list = []
    if len(st.session_state['vacations_list']) != 0:
        vacations_list = [add.split(',') for add in st.session_state['vacations_list']]
    
    st.write('---')

    # Calculations

    df_nothing = calc_credit(st.session_state['settings'], [], change_wibor_list, [], [['2099-01' ,item[1]] for item in vacations_list])
    
    df = calc_credit(st.session_state['settings'], add_principle_list, change_wibor_list, short_term_list, vacations_list )
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4, vertical_alignment="bottom")
    delta_tmp = df[-1]['interest_sum'] - df_nothing[-1]['interest_sum']
    if delta_tmp != 0:
        col1.metric(language['total_interest'], f"{df[-1]['interest_sum']:,.0f}",delta=f"{delta_tmp:,.0f}", delta_color="inverse", border=True)
    else:
        col1.metric(language['total_interest'], f"{df[-1]['interest_sum']:,.0f}", border=True)
    df_new_paid = df[df['perc'] >= 0]
    df_new_paid = df_new_paid[df_new_paid['payments_number'] >= 0]
    col2.metric(label=language['payoff_date'],value=np.datetime_as_string(df_new_paid[-1]['date'], "M"), border=True)
    col3.metric(label=language['sum_additional_payments'],value=str(round(df_new_paid['add_principle'].sum())), border=True)
    col4.metric(label=language['perc_additional_payments'],value=str(round(round(df_new_paid['add_principle'].sum()) / st.session_state['settings']['credit_principle'] * 100, 2)) + '%', border=True)
    
    # Combine both df and df_nothing for df_chart

    df_chart = np.zeros((df_nothing.shape[0])
    , dtype=[
        ('date', 'datetime64[M]'),
        ('credit_principle', 'f8'),
        ('interest_sum', 'f8'),
        ('installment', 'f8'),
        ('perc', 'f8'),
        ('credit_principle_adj', 'f8'),
        ('interest_sum_adj', 'f8'),
        ('installment_adj', 'f8'),
        ('perc_adj', 'f8'),
    ])

    for i in range(0, df_nothing.shape[0]):
        
        index_tmp = df.shape[0]
        if i < index_tmp:
            df_chart[i]['date'] = df_nothing[i]['date']
            df_chart[i]['credit_principle'] = df_nothing[i]['credit_principle']
            df_chart[i]['interest_sum'] = df_nothing[i]['interest_sum']
            df_chart[i]['installment'] = df_nothing[i]['installment']
            df_chart[i]['perc'] = df_nothing[i]['perc']

            df_chart[i]['credit_principle_adj'] = df[i]['credit_principle']
            df_chart[i]['interest_sum_adj'] = df[i]['interest_sum']
            df_chart[i]['installment_adj'] = df[i]['installment']
            df_chart[i]['perc_adj'] = df[i]['perc']
        else:
            df_chart[i]['date'] = df_nothing[i]['date']
            df_chart[i]['credit_principle'] = df_nothing[i]['credit_principle']
            df_chart[i]['interest_sum'] = df_nothing[i]['interest_sum']
            df_chart[i]['installment'] = df_nothing[i]['installment']
            df_chart[i]['perc'] = df_nothing[i]['perc']

            df_chart[i]['credit_principle_adj'] = df[-1]['credit_principle']
            df_chart[i]['interest_sum_adj'] = df[-1]['interest_sum']
            df_chart[i]['installment_adj'] = df[-1]['installment']
            df_chart[i]['perc_adj'] = df[-1]['perc']

    # Chart

    df_chart = pd.DataFrame(df_chart)
    st.line_chart(df_chart, x="date", y=["credit_principle", "interest_sum", "credit_principle_adj", "interest_sum_adj"], color=["#ffaa00", "#00674F","#ffe150", "#3d85c6"], x_label='')

    # Chart installement or percent
    if st.session_state['perc_toggle']:
        st.line_chart(df_chart, x="date", y=["perc", "perc_adj"], color=["#ffe150", "#3d85c6"], x_label='')
    else:
        st.line_chart(df_chart, x="date", y=["installment", "installment_adj"], color=["#ffe150", "#3d85c6"], x_label='')

    # Summary Tables
    with st.expander(language['summary_table'], expanded=True):
        st.dataframe(df)

    with st.expander(language['summary_table_nothing']):
        st.dataframe(df_nothing)

    st.write('---')
    st.markdown(language['disclaimer'])
    
    # st.session_state