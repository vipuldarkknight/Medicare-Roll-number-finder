##hospital search hppy path
* greet
  - find_facility_types
* inform{"facility_type": "hospital"}    
    - facility_form
    - form{"name": "facility_form"}
    - form{"name": null}
* inform{"facility_id": "81"}
    - find_healthcare_address
    - utter_address
* thanks
  - utter_goodbye

##happy_path_multi_requests
* greet
  - find_facility_types
* inform{"facility_type": "Medical"}
    - facility_form
    - form{"name": "facility_form"}
    - form{"name": null}
* inform{"facility_id": "74"}
    - find_healthcare_address
    - utter_address
* search_request{"facility_type": "Medical"}
    - facility_form
    - form{"name": "facility_form"}
    - form{"name": null}
* inform{"facility_id": "450"}   
    - find_healthcare_address
    - utter_address

## happy_path2
* search_request{"location": "Jaipur", "facility_type": "hospital"}
    - facility_form
    - form{"name": "facility_form"}
    - form{"name": null}
* inform{"facility_id": "25"}
    - find_healthcare_address
    - utter_address
* thanks
  - utter_goodbye

## rollnumber finder1
* greet
  - utter_greet_botdescription
* roll_finder{"name": "Vipul Agarwal"}
  - action_findroll
  - utter_ask
* inform{"booln":"Yes"}
  - utter_pos_goodbye

## rollnumber finder1
* greet
  - utter_greet_botdescription
* roll_finder{"name": "Vipul Agarwal"}
  - action_findroll
  - utter_ask
* inform{"booln":"No"}
  - utter_neg_goodbye

## story_thankyou
* thanks
  - utter_pos_goodbye

## say goodbye
* goodbye
  - utter_goodbye

## bot challenge
* bot_challenge
  - utter_iamabot
