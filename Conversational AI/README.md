# Work on Conversational AI/Chat Bots
## Experience
Starting in April 2020, I started working as an NLP Intern at a Seattle startup called Seasalt.AI. I finished my internship in September, and am presently still working at Seasalt part-time. Seasalt is a Conversational AI and Speech tech company. I was hired to create their first demo bot that they could show to potential business customers. Through working on this project I got to work hands-on with Rasa Open Source and Kubernetes. In addition to gaining a deep understanding of Rasa (and getting a certification), I also build on top of Rasa and developed my own dialogue management policy and cart backend for e-commerce bots. 

## Projects
### Rule-based Dialogue Manager - Rasa Policy
The rule-based policy I developed (*ngChatPolicy*) is a simple finite-state machine-like dialogue manager. It reads in a yaml file with states; each state contains a list of conditions, and a set of actions to execute if the state is chosen as the best state. This policy can be used in conjunction with existing Rasa policies, including TEDPolicy, or can be used as a stand-alone dialogue manager. See the [readme]('./Policy/README.md') and the [source code]('./Policy/policy.py').

### Backend Cart Management System for e-Commerce Bots
### Starbucks Bot