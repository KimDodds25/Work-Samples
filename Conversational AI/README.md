# Work on Conversational AI/Chat Bots
## Experience
Starting in April 2020, I started working as an NLP Intern at a Seattle startup called Seasalt.AI. I finished my internship in September, and am presently still working at Seasalt part-time. Seasalt is a Conversational AI and Speech tech company. I was hired to create their first demo bot that they could show to potential business customers. Through working on this project I got to work hands-on with Rasa Open Source and Kubernetes. In addition to gaining a deep understanding of Rasa (and getting a certification), I also build on top of Rasa and developed my own dialogue management policy and cart backend for e-commerce bots. 

## Projects:
## Rule-based Dialogue Manager - Rasa Policy
The rule-based policy I developed (*ngChatPolicy*) is a simple finite-state machine-like dialogue manager. It reads in a yaml file with states; each state contains a list of conditions, and a set of actions to execute if the state is chosen as the best state. This policy can be used in conjunction with existing Rasa policies, including TEDPolicy, or can be used as a stand-alone dialogue manager. See the [readme]('./Policy/README.md') and the [source code]('./Policy/policy.py').

## Backend Cart Management System for e-Commerce Bots
The cart management system (*ngChatCart*), provides a generalized cart implementation that be integrated into any chat bot. cart.py includes classes for the cart and menu, as well as classes for items and options. Callable methods cover a wide range of capabilities, including but not limited to: setting a menu, describing menu categories/items, adding/removing items from the cart, caching user carts for multi-user support, etc.
Also included is a generalized menu schema which allows a wide variety of food-service business use cart.py with no modifications to the source code.

cart.py originated as my project, but later received modifications by two of my colleagues. Regardless, the majority of the code was written by me, and all other addition were approved by myself.

ngChatCart source code is not available to the public yet, but I have included the README and sphinx documentation.

## Starbucks Bot
The Starbucks bot was built to demonstrate the capabilities of an e-commerce bot for food and beverage ordering. The bot is built with Rasa Open Source and also uses ngChatPolicy and ngChatCart. Capabilities of the bot include answering queries about the menu (categories, items, item options, etc), giving item recommendations, taking complex item orders and storing them in a cart, modifying and removing items in the cart, and 'checking out' (no purchases are actually made through this bot). The bot is publicly accessible through Facebook [here](m.me/103266051434683). Please note that the bot is *still under development*, and as such, may experience down time or bugs as we try out new features. 