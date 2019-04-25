## API server


## API list

/history_patient
- input
    Pid : str(Patient ID)
 -output
    Result : Result : str (“Success” or “Fail”)
    * In case of Success
    Notes : list of dictionary( keys: [note_id, date, contents])


/cervical_spine_cb
- input  
    Pid : str(patient ID)  
- output   
    Result : Result : str (“Success” or “Fail”)
    Pid : str("patient ID")
    * In case of Success     
    Target : str (“{target_name}”)  
    Sentence : str ( “text contents lesser than 255 chracter”)  
  

/find_feature  
- input  
    Pid : str
    F_list : list of str ( target feature list to extract)
    Start_date : str (YYYY-MM-DD)
    End_date : str (YYYY-MM-DD)
- output   
    Result : str (“Success” or “Fail”)
    * In case of Fail
    resion : 
    
    * In case of Success
    Info : dictionary (   
        key : input에서 들어온 모든 feature 들  
        value : dictionary ( “result” : True, “sentences”:list of str)  
    )