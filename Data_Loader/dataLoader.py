#-*- coding: utf-8 -*-
"Proof connection at pyodbc level."
import pandas as pd
import pyodbc
import getpass

class DBConnector:

    conn = None
    pwd = None

    @staticmethod
    def make_conn():

        if DBConnector.username is None:
            DBConnector.username = getpass.getuser("Partners Username: ")

        if DBConnector.pwd is None:
            DBConnector.pwd = getpass.getpass("We need DB Password! : ")

        conn = pyodbc.connect(driver='FreeTDS',
                              TDS_version="7.1",
                              host='phsedw.partners.org,1433',
                              user='PARTNERS\\{}'.format(DBConnector.username),
                              # charset='utf8',
                              pwd=DBConnector.pwd)

        return conn

    @staticmethod
    def get_db_conn():
        try:
            conn = DBConnector.conn
            cursor = conn.cursor()
            cursor.execute('Use Epic;')
        except:
            DBConnector.conn = DBConnector.make_conn()
            DBConnector.conn = DBConnector.get_db_conn()
        return DBConnector.conn

conn = DBConnector.get_db_conn()

def get_accessible_views(conn):
    query = '''
    SELECT s.name AS SchemaName, v.name AS ViewName,s.schema_id, v.object_id 
    FROM sys.views v 
    INNER JOIN sys.schemas s ON s.schema_id = v.schema_id;'''
    df_view = pd.read_sql(query, conn)
    return df_view


def get_list_zid_from_idtable(mrn, hospital_name):
    '''
    :param mrn:
    :return:
    '''
    '''MGH : 67, 227
    BWH : 69, 251
    FH : 118, 228
    NWH : 48, 226
    '''
    if hospital_name == "MGH":
        hospital_id = [67, 227]
    elif hospital_name == "BWH":
        hospital_id = [69, 251]
    elif hospital_name == "FH":
        hospital_id = [118, 228]
    elif hospital_name == "NWH":
        hospital_id = [48, 226]
    else:
        print("[Error] Wrong hospital name: {}".format(hospital_name))
        hospital_id = [-1, -1]

    query = '''SELECT *
      FROM [Epic].[Patient].[IDENTITY_PHS]
      WHERE (PatientIdentityID = '{}') and (IdentityTypeID = '{}' or IdentityTypeID = '{}');'''.format(mrn, hospital_id[0], hospital_id[1])

    df_view = pd.read_sql(query, conn)
    z_pid_table = df_view.groupby('PatientID').count()
    z_pid_table['PatientID'] = z_pid_table.index
    return z_pid_table

def xstr(s):
    if s is None:
        return ''
    return str(s)

def get_list_zid_from_pttable(patient_id):
    conn = DBConnector.get_db_conn()
    query = "SELECT * FROM Epic.Patient.Patient_PHS WHERE MRN = '{}';".format(patient_id)
    patient_info = pd.read_sql(query, conn)
    return patient_info

def get_noteid_list(patient_id, hospital):
    if hospital is None:
        hospital = "MGH"

    print("patientid({}) hospital({}) is requested".format(patient_id, hospital))

    patient_info_from_pt_table = get_list_zid_from_pttable(patient_id)
    patient_info_from_id_table = get_list_zid_from_idtable(patient_id, hospital)

    all_patient_z_id = list(patient_info_from_pt_table['PatientID']) + list(patient_info_from_id_table['PatientID'])
    all_patient_z_id = list(set(all_patient_z_id))
    all_num = len(all_patient_z_id)

    print("{} patient ID found : ".format(all_num), patient_info_from_pt_table.shape[0], len(patient_info_from_id_table))

    if all_patient_z_id :
        print(all_patient_z_id)

    tmp_df = pd.DataFrame(columns=['NoteID'])

    if all_num == 0:
        return tmp_df

    for z_p_id in all_patient_z_id:
        query = "SELECT * FROM Epic.Clinical.Note_PHS WHERE PatientLinkID = '{}'".format(z_p_id)
        noteid_by_link = pd.read_sql(query, conn)
        print("NoteID counted in {} : ".format(z_p_id), noteid_by_link.shape[0])
        tmp_df = tmp_df.append(noteid_by_link, ignore_index=True)

    # result_df = tmp_df.sort_values(['NoteID', 'EDWLastModifiedDTS'], ascending=False).tail(500)
    result_df = tmp_df.sort_values(['NoteID', 'EDWLastModifiedDTS'], ascending=False)
    # print("Cols : ", result_df.columns)
    print("Result shape : ", result_df.shape)
    return result_df

def get_notetext_from_noteid(noteid_by_link):
    ## Make final note_df
    cols = ['ContactDTS', 'NoteTXT', 'NoteID', 'NoteCSNID', 'LineNBR', 'EDWLastModifiedDTS']
    note_df = pd.DataFrame(columns=cols)
    conn = DBConnector.get_db_conn()

    for note_csnid in noteid_by_link['NoteID']:
        query = "SELECT * FROM Epic.Clinical.NoteText_PHS where NoteID = '{}'".format(note_csnid)
        note_text_df = pd.read_sql(query, conn)
        if note_text_df.shape[0]:
            note_df = note_df.append(note_text_df, ignore_index=False)

    if note_df.shape[0] == 0:
        return []

    target_df = note_df[cols].sort_values(['NoteID', 'EDWLastModifiedDTS', 'NoteCSNID', 'LineNBR'])

    ## Merge all same noteCSNID
    stack = {
        'id': None,
        'csn_id': None,
        'text': None,
        'date': None,
    }

    content_list = []

    for index, row in target_df.iterrows():
        text = xstr(row['NoteTXT'])
        note_id = row['NoteID']
        note_csnid = row['NoteCSNID']
        last_mod = row['EDWLastModifiedDTS']
        date = str(row['ContactDTS'])[:10]

        if stack['id'] is None:
            stack['id'] = note_id
            stack['csn_id'] = note_csnid
            stack['text'] = text
            stack['date'] = date
            stack['last_mod'] = last_mod
        elif stack['csn_id'] == note_csnid:
            try:
                stack['text'] = "".join([stack['text'], text])
            except Exception as e:
                print("Error : ", e)
                print('note_csnid:', note_csnid)
                print('csn_id:', stack['csn_id'])
                print("Stack:", stack['text'])
                print("Text: ", stack['text'])
                print("Row:", row)
                print("Xstr(row_txt):", text)
        else:
            paragraph = stack['text']
            paragraph_id = stack['id']
            paragraph_csnid = stack['csn_id']
            paragraph_date = stack['date']
            paragraph_lastmod = stack['last_mod']

            stack['id'] = note_id
            stack['csn_id'] = note_csnid
            stack['text'] = text
            stack['date'] = date
            stack['last_mod'] = last_mod

            content_list.append({
                'note_id': paragraph_id,
                'noteCSN_id': paragraph_csnid,
                'category': 'visit_note',
                'date': paragraph_date,
                'last_mod': paragraph_lastmod,
                'contents': paragraph,
            })

    ## Add last one row
    if stack['id'] is not None:
        paragraph = stack['text']
        paragraph_id = stack['id']
        paragraph_csnid = stack['csn_id']
        paragraph_date = stack['date']
        paragraph_lastmod = stack['last_mod']

        content_list.append({
            'note_id': paragraph_id,
            'noteCSN_id': paragraph_csnid,
            'category': 'visit_note',
            'date': paragraph_date,
            'last_mod': paragraph_lastmod,
            'contents': paragraph,
        })

    # sorted_list_by_date = sorted(content_list, key=lambda k: k['date'])
    print("{} notes are collected,".format(len(content_list)))

    ## Delete all duplicates notes
    print("Drop duplicates")
    df = pd.DataFrame(content_list).sort_values(['note_id', 'last_mod'])
    df = df.drop_duplicates('note_id', keep='last')

    result_list = []
    for index, row in df.iterrows():
        result_list.append({
            'note_id': row['note_id'],
            'noteCSN_id': row['noteCSN_id'],
            'category': row['category'],
            'date': row['date'],
            'last_mod': row['last_mod'],
            'contents': row['contents'],
        })

    sorted_list_by_date = sorted(result_list, key=lambda k: k['date'], reverse=True)
    print("{} notes remain.".format(len(result_list)))

    return sorted_list_by_date


def check_access_db():
    ## Check accessibility and Use EPIC.
    conn = DBConnector.get_db_conn()
    df_view = get_accessible_views(conn)
    print("{} views are accesible.".format(df_view.shape[0]))


def load_all_data(patient_id, hospital=None):
    ## params : pareint_id : int

    ## Check accessibility and Use EPIC.
    check_access_db()

    ## Get NoteID list by pateint_id
    note_ids = get_noteid_list(patient_id, hospital)

    ## Get Note Text from Note ID as list of dict(date, NoteTXT)
    all_text_list = get_notetext_from_noteid(note_ids)

    return all_text_list


if __name__ == "__main__":
    ## Test for 1 Patient
    mrn= '3414207'
    all_list = load_all_data(mrn)

    # list_df = [pd.DataFrame(d) for d in all_list]
    df_hx = pd.DataFrame(all_list, columns=['category', 'date', 'note_id', 'contents'])
    df_hx['date'] = pd.to_datetime(df_hx['date'])
    df_hx = df_hx.sort_values(by='date')
    print(df_hx.shape)

    df_hx.to_csv('tmp_{}.csv'.format(mrn), index=False, encoding='utf8')

