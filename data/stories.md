##hospital search hppy path  
* greet
  - find_language_type
* inform{"language": "Hindi"}
    - find_facility_types
* inform{"facility_type": "hospital"}    
    - facility_form
    - form{"name": "facility_form"}
    - form{"name": null}
* inform{"facility_id": "81"}
    - find_healthcare_address
    - action_say_address
    - action_anything_else
* deny    
    - action_ask_feedback
* feedback{"feedback_value": "positive"}
    - slot{"feedback_value": "positive"}
    - action_great
* goodbye
    - action_goodbye

##happy_path_multi_requests
* greet
  - find_language_type
* inform{"language": "Hindi"}
    - find_facility_types
* inform{"facility_type": "Medical"}
    - facility_form
    - form{"name": "facility_form"}
    - form{"name": null}
* inform{"facility_id": "74"}
    - find_healthcare_address
    - action_say_address
    - action_anything_else
* search_request{"facility_type": "Medical"}
    - facility_form
    - form{"name": "facility_form"}
    - form{"name": null}
* inform{"facility_id": "450"}   
    - find_healthcare_address
    - action_say_address
    - action_anything_else
* deny    
    - action_ask_feedback
* feedback{"feedback_value": "positive"}
    - slot{"feedback_value": "positive"}
    - action_great

## happy_path2
* search_request{"location": "Jaipur", "facility_type": "hospital"}
    - find_language_type
    - facility_form
    - form{"name": "facility_form"}
    - form{"name": null}
* inform{"facility_id": "25"}
    - find_healthcare_address
    - action_say_address
    - action_anything_else
* deny    
    - action_ask_feedback
* feedback{"feedback_value": "positive"}
    - slot{"feedback_value": "positive"}
    - action_great
* thanks
  - action_goodbye


## anything else? - yes
    - action_anything_else
* affirm
    - action_what_help

## anything else? - no
    - action_anything_else
* deny
    - utter_thumbsup

## positive reaction
* react_positive
    - utter_react_positive

## negative reaction
* react_negative
    - utter_react_negative

## greet + handoff + lang
* greet
    - find_language_type
* inform{"language": "Hindi"}
    - find_facility_types
* human_handoff
    - action_contact_email

## greet + handoff + nolang
* greet
    - find_language_type
* human_handoff
    - action_contact_email

## chitchat
* human_handoff
    - action_contact_email

## out of scope
* out_of_scope
    - respond_out_of_scope
    - utter_possibilities

## rollnumber finder1
* greet
  - find_language_type
* inform{"language": "Hindi"}
    - find_facility_types
* roll_finder{"name": "Vipul Agarwal"}
  - action_findroll
  - utter_ask
* inform{"result":"positive"}
  - utter_pos_goodbye

## rollnumber finder1
* greet
  - find_language_type
* inform{"language": "Hindi"}
    - find_facility_types
* roll_finder{"name": "Vipul Agarwal"}
  - action_findroll
  - utter_ask
* inform{"result":"negative"}
  - utter_neg_goodbye

## story_thankyou
* thanks
  - utter_noworries
  - action_anything_else

## say goodbye
* goodbye
  - action_goodbye

## story number 6
* greet
    - find_language_type
* inform{"language": "Hindi"}
    - find_facility_types
* chitchat
    - respond_chitchat
* chitchat
    - respond_chitchat

## story number 14
* greet
    - find_language_type
* greet
    - find_facility_types
* chitchat
    - respond_chitchat
* chitchat
    - respond_chitchat

## story number 17
* greet
    - find_language_type
* deny
    - utter_nohelp
* out_of_scope
    - respond_out_of_scope
    - utter_possibilities
* chitchat
    - respond_chitchat
* chitchat
    - respond_chitchat
* chitchat
    - respond_chitchat
* chitchat
    - respond_chitchat

## Story from conversation with 29d264d8ce574a11bde572f0e79b73f3 on November 19th 2018
* greet
    - find_language_type
* greet
    - find_facility_types
* chitchat
    - respond_chitchat
* affirm
    - utter_thumbsup


