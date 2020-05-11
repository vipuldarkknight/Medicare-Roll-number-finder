## feedback1
    - action_ask_feedback
* out_of_scope
    - utter_thumbsup
    - action_anything_else

## feedback3
    - action_ask_feedback
* affirm
    - action_great
    - action_anything_else

## feedback deny
    - action_ask_feedback
* deny
    - utter_thumbsup
    - action_anything_else

## feedback thanks
    - action_ask_feedback
* thanks
    - utter_noworries
    - action_anything_else

## feedback thumbsup
    - action_ask_feedback
* feedback{"feedback_value": "negative"}
    - slot{"feedback_value": "negative"}
    - utter_thumbsup
    - action_anything_else

## feedback thumbsup
    - action_ask_feedback
* feedback{"feedback_value": "positive"}
    - slot{"feedback_value": "positive"}
    - action_great
    - action_anything_else
