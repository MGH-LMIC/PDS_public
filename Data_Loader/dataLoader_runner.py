
from dataLoader import *

if __name__ == "__main__":
    # ## -----------------------
    # ## Load all real patients
    # ## -----------------------
    # mrn_df = pd.read_excel('../data/Cerv_Spine_Evals_MGH-1.xlsx', dtype=str)
    #
    # print(mrn_df.columns)
    # print(mrn_df.shape)
    # print(mrn_df.head())
    #
    # for index, row in mrn_df.iterrows():
    #     mrn = row['MRN']
    #     print("MRN : ", mrn)
    #     all_list = load_all_data(mrn)
    #
    #     # list_df = [pd.DataFrame(d) for d in all_list]
    #     df_hx = pd.DataFrame(all_list, columns=['category', 'date', 'note_id', 'contents'])
    #     df_hx['date'] = pd.to_datetime(df_hx['date'])
    #     df_hx = df_hx.sort_values(by='date', ascending=False)
    #     df_hx = df_hx.applymap(lambda x: x.encode('unicode_escape').decode('utf-8') if isinstance(x, str) else x)
    #
    #     print(df_hx.shape)
    #
    #     if df_hx.shape[0]:
    #         df_hx.to_excel('../data/result/sample_hx_1218_{}.xlsx'.format(mrn), index=False, encoding='utf-8')
    #     else:
    #         print("No data to save! MRN:", mrn)

    ## -----------------------
    ## Load all real patients
    ## -----------------------
    mrn_df = pd.read_csv('../data/Combined_Cerv_Eval_nonan.csv', dtype=str)

    print(mrn_df.columns)
    print(mrn_df.shape)
    print(mrn_df.head())

    for index, row in mrn_df.iterrows():
        mrn = row['MRN_db']
        hospital = row['Site'].strip()
        if row['MRN_old'] == 'FAKE' or pd.isnull(row['MRN_db']):
            continue
        print("MRN : ", mrn)
        print("MRN_old : ", row['MRN_old'])
        print("Hostptal : ", hospital)


        all_list = load_all_data(mrn, hospital)
        df_hx = pd.DataFrame(all_list, columns=['category', 'date', 'note_id', 'contents'])
        df_hx['date'] = pd.to_datetime(df_hx['date'])
        df_hx = df_hx.sort_values(by='date', ascending=False)
        df_hx = df_hx.applymap(lambda x: x.encode('unicode_escape').decode('utf-8') if isinstance(x, str) else x)

        print(df_hx.shape)

        if df_hx.shape[0]:
            df_hx.to_excel('../data/result/sample_hx_0103_{}.xlsx'.format(mrn), index=False, encoding='utf-8')
        else:
            print("No data to save! MRN:", mrn)

    # ## -----------------------
    # ## Load all test patient
    # ## -----------------------
    # mrn_df = pd.read_excel('../data/TestPatients.xlsx', dtype=str)
    # print(mrn_df.columns)
    # print(mrn_df.shape)
    # print(mrn_df.head())
    #
    # for index, row in mrn_df.iterrows():
    #     mrn = row['MGHMRN']
    #     print("MRN : ", mrn)
    #     all_list = load_all_data(mrn)
    #
    #     # list_df = [pd.DataFrame(d) for d in all_list]
    #     df_hx = pd.DataFrame(all_list, columns=['category', 'date', 'note_id', 'contents'])
    #     df_hx['date'] = pd.to_datetime(df_hx['date'])
    #     df_hx = df_hx.sort_values(by='date')
    #     df_hx = df_hx.applymap(lambda x: x.encode('unicode_escape').decode('utf-8') if isinstance(x, str) else x)
    #
    #     print(df_hx.shape)
    #
    #     if df_hx.shape[0]:
    #         df_hx.to_excel('../data/result_testpt/sample_hx_1218_{}.xlsx'.format(mrn), index=False, encoding='utf8')
    #     else:
    #         print("No data to save! MRN:", mrn)
