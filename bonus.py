

def convertSubtaskToScript(actions: list[str], previous_subtasks: list[list[str]], feedback: str) -> list[str]:
    """
    Generates a Playwright script for an entire subtask using an LLM.
    Learns from previous subtask scripts and feedback to improve accuracy.

    Args:
        actions: List of action descriptions in the subtask
        previous_subtasks: List of previously generated subtask scripts that was unsuccessful so LLM can learn from them
        feedback: Diagnostic feedback from previous test failures
        Note: if previous_subtasks is empty and thee feedback is "", the LLM should generate a script from scratch

    Returns:
        list[str]: Generated Playwright scripts for the entire subtask
    """
    # LLM generates scripts for all actions in the subtask at once

    return list_of_generated_playwrite_scripts


def testSingleSubtask(established_scripts: list[str], new_subtask_scripts: list[str], idx: int) -> str:
    """
    Validates if executing the subtask scripts achieves the expected state transition

    Returns:
        str: "1" if successful, else LLM-generated different description
    """
    target_before = demo['transition_descriptions'][idx]['before_state_description']
    target_after = demo['transition_descriptions'][idx]['after_state_description']

    # Reset to initial state
    reset_browser()
    
    # Execute established workflow to reach expected "before" state
    for script in established_scripts:
        execute_script(script)

    # Verify starting point matches expected "before" state
    current_state = analyze_current_state()
    if not LLM.compare_states(current_state, target_before):
        return f"Initial state mismatch: {LLM.describe_state_diff(current_state, target_before)}"

    # Execute new subtask scripts
    for script in new_subtask_scripts:
        execute_script(script)

    # Verify final state matches expected "after" state
    current_state = analyze_current_state()
    if LLM.compare_states(current_state, target_after):
        return "1"
    return LLM.describe_state_diff(current_state, target_after)


def mainLoop():
    verified_script_sequence = []  # All validated subtask scripts
    current_subtask_scripts = []  # Scripts for current subtask being tested
    diagnostic_feedback = ""
    transition_idx = 0  # Index for state transitions

    for subtask in demo['trajectory_decomposition']['subtasks']:
        actions = subtask['action_description']['action_descriptions']
        
        while True:
            # Generate full subtask scripts using LLM (all actions at once)
            current_subtask_scripts = convertSubtaskToScript(
                actions=actions,
                previous_generation=current_subtask_scripts,
                feedback=diagnostic_feedback
            )
            
            # Test the complete subtask implementation
            test_result = testSingleSubtask(
                established_scripts=verified_script_sequence,
                new_subtask_scripts=current_subtask_scripts,
                idx=transition_idx
            )

            if test_result == "1":
                # Commit successful subtask scripts
                verified_script_sequence.extend(current_subtask_scripts)
                current_subtask_scripts = []
                diagnostic_feedback = ""
                break
            else:
                # Update feedback for retry
                diagnostic_feedback = test_result

        transition_idx += 1

# Execute the workflow
mainLoop()



demo = {
    "trajectory_decomposition": {
        "trajectory_description": "The user navigates and interacts with UberEats to find and select popular food items from a specific restaurant.",
        "subtasks": [
            {
                "action_description": {
                    "description": "Navigate to UberEats and close location modal.",
                    "action_ids": [
                        0,
                        1
                    ],
                    "action_descriptions": [
                        "URL navigation to https://www.ubereats.com/",
                        "Click on the close button of location access modal."
                    ]
                },
                "transition_description": "A modal appears prompting the user to allow location access, but was closed, displaying options for entering a delivery address and searching for food."
            },
            {
                "action_description": {
                    "description": "Enter and select the delivery address.",
                    "action_ids": [
                        2,
                        3,
                        4
                    ],
                    "action_descriptions": [
                        "Click on the delivery address input field.",
                        "Type '2390 el camino real' into the delivery address input field.",
                        "Click on the suggested address '2390 El Camino Real'."
                    ]
                },
                "transition_description": "User entered and selected the delivery address, which updated the page to show food delivery options specific to that address."
            },
            {
                "action_description": {
                    "description": "Navigate to Chipotle Mexican Grill page.",
                    "action_ids": [
                        5
                    ],
                    "action_descriptions": [
                        "Click on Chipotle Mexican Grill to view its menu and details."
                    ]
                },
                "transition_description": "The page transitioned from general food options to Chipotle Mexican Grill's specific menu page."
            },
            {
                "action_description": {
                    "description": "Explore and interact with Chipotle Mexican Grill menu items.",
                    "action_ids": [
                        6,
                        7,
                        8,
                        9,
                        10,
                        11,
                        12
                    ],
                    "action_descriptions": [
                        "Scroll to explore featured items.",
                        "Click on the '#1 most liked' item to view details.",
                        "Close the detailed view of the Burrito Bowl.",
                        "Click on the '2nd most liked' item to view details.",
                        "Close the detailed view of the Burrito.",
                        "Click on the '#3 most liked' item to view details.",
                        "Closed the Quesadilla details view."
                    ]
                },
                "transition_description": "The user explores featured menu items by viewing details of the several most liked options and toggling views to return to the full menu. The arrangement of items and featured selections updates accordingly. No visible page changes occurred after the final closing action. "
            }
        ]
    },
    "transition_descriptions": [
        {
            "before_state_description": {
                "website": "Uber Eats",
                "overview": "The loading page of Uber Eats where users can order food.",
                "functional_analysis": "This page is designed for users to enter their delivery address and access food delivery options.",
                "functional_actions": [
                    "Enter delivery address",
                    "Sign in"
                ]
            },
            "after_state_description": {
                "website": "Uber Eats",
                "overview": "The Uber Eats homepage after loading, showing a location permission request modal.",
                "functional_analysis": "The page now includes a modal prompting the user to allow location access for a more personalized experience by showing nearby restaurants.",
                "functional_actions": [
                    "Allow location access",
                    "Enter delivery address instead",
                    "Sign in"
                ]
            },
            "transition_description": "A modal appears prompting the user to allow location access, enhancing the food ordering experience by potentially showing nearby restaurants."
        },
        {
            "before_state_description": {
                "website": "Uber Eats",
                "overview": "The home page for Uber Eats, prompting users to enter a delivery address to view restaurants.",
                "functional_analysis": "This page allows users to enter a delivery address to explore nearby restaurants for food delivery. Users can also see options to sign in or log in to their accounts.",
                "functional_actions": [
                    "Enter delivery address",
                    "Log in",
                    "Sign up"
                ]
            },
            "after_state_description": {
                "website": "Uber Eats",
                "overview": "The home page for Uber Eats shows options for inputting delivery address and searching for food without location permission.",
                "functional_analysis": "The page now prominently displays a field to enter a delivery address and buttons for immediate delivery options. The previous location permission prompt is no longer visible, allowing users to search directly.",
                "functional_actions": [
                    "Enter delivery address",
                    "Deliver now",
                    "Search here",
                    "Log in",
                    "Sign up"
                ]
            },
            "transition_description": "The location permission modal was closed after the user clicked the close button, allowing the main content page to display options for directly entering a delivery address and searching for food."
        },
        {
            "before_state_description": {
                "website": "Uber Eats",
                "overview": "The homepage allows users to order food delivery and enter their delivery address.",
                "functional_analysis": "This page is primarily used for ordering food from local restaurants. It features an address input field, delivery options, and sign-in options.",
                "functional_actions": [
                    "Enter delivery address",
                    "Choose delivery time",
                    "Search for restaurants",
                    "Sign in",
                    "Sign up"
                ]
            },
            "after_state_description": {
                "website": "Uber Eats",
                "overview": "The homepage allows users to order food delivery and enter their delivery address.",
                "functional_analysis": "This page is primarily used for ordering food from local restaurants. It features an address input field, delivery options, and sign-in options.",
                "functional_actions": [
                    "Enter delivery address",
                    "Choose delivery time",
                    "Search for restaurants",
                    "Sign in",
                    "Sign up"
                ]
            },
            "transition_description": "The input field for entering the delivery address was clicked, resulting in the element being active, which may allow for user interaction such as typing an address."
        },
        {
            "before_state_description": {
                "website": "Uber Eats",
                "overview": "The homepage of Uber Eats featuring a food delivery interface.",
                "functional_analysis": "This page allows users to enter their delivery address to find available food delivery options nearby.",
                "functional_actions": [
                    "Enter delivery address",
                    "Select delivery time",
                    "Search for food",
                    "Sign in or sign up"
                ]
            },
            "after_state_description": {
                "website": "Uber Eats",
                "overview": "The homepage of Uber Eats with search results for a delivery address.",
                "functional_analysis": "The page now shows suggested delivery addresses based on the user input.",
                "functional_actions": [
                    "Enter delivery address",
                    "Select delivery time",
                    "Search for food",
                    "Sign in or sign up",
                    "Clear search selection"
                ]
            },
            "transition_description": "After typing '2390 el camino real' into the delivery address input field, a dropdown list appears showing multiple address suggestions related to the input, including '2390 El Camino Real, Palo Alto, CA', along with other nearby locations. This change allows users to select a suggested address for more efficient searching."
        },
        {
            "before_state_description": {
                "website": "Uber Eats",
                "overview": "The page allows users to order food delivery from local restaurants. It prominently features options to select a delivery address and browse nearby restaurants.",
                "functional_analysis": "Users can input their delivery address, view nearby restaurants based on that address, and start their order process.",
                "functional_actions": [
                    "Enter delivery address",
                    "View nearby restaurants",
                    "Select a restaurant",
                    "Start an order"
                ]
            },
            "after_state_description": {
                "website": "Uber Eats",
                "overview": "The page now displays food delivery options based on the selected address, including promotional offers, different food categories, and popular restaurants.",
                "functional_analysis": "Users can view food delivery options, special promotions, and filter restaurants by various categories.",
                "functional_actions": [
                    "Browse food categories",
                    "View offers",
                    "Order food from selected restaurants",
                    "Filter by rating, price, and dietary options",
                    "Access shopping cart"
                ]
            },
            "transition_description": "After clicking on the address '2390 El Camino Real', the page transitioned to show food delivery options specific to that address. This included promotional offers and categories for various types of food, enhancing the ordering experience with new filters and suggestions."
        },
        {
            "before_state_description": {
                "website": "Uber Eats",
                "overview": "A food delivery and pickup service offering a variety of restaurants to choose from.",
                "functional_analysis": "Allows users to browse and order food from local restaurants with filtering options for different cuisines and deals.",
                "functional_actions": [
                    "View offers",
                    "Order food",
                    "Filter by dietary needs",
                    "Search for restaurants",
                    "View delivery time and fees"
                ]
            },
            "after_state_description": {
                "website": "Uber Eats",
                "overview": "The page for Chipotle Mexican Grill with details on menu, ratings, and delivery options.",
                "functional_analysis": "Provides specific information about Chipotle Mexican Grill including menu items, reviews, location, and delivery options.",
                "functional_actions": [
                    "Order food from Chipotle",
                    "View menu items",
                    "Read reviews",
                    "View location on map",
                    "Select delivery or pickup options"
                ]
            },
            "transition_description": "The user clicked on the Chipotle Mexican Grill name, transitioning from the general food selection page to the specific restaurant page featuring Chipotle's menu, ratings, and delivery details."
        },
        {
            "before_state_description": {
                "website": "Uber Eats",
                "overview": "Chipotle Mexican Grill page showing location, rating, and reviews.",
                "functional_analysis": "This page allows users to view the menu, rating, reviews, and order food from Chipotle Mexican Grill.",
                "functional_actions": [
                    "View menu items",
                    "Read reviews",
                    "See ratings",
                    "Place an order"
                ]
            },
            "after_state_description": {
                "website": "Uber Eats",
                "overview": "Updated view of Chipotle Mexican Grill showcasing featured items and operational details.",
                "functional_analysis": "This page now highlights featured menu items for easier ordering, including prices and popularity ratings.",
                "functional_actions": [
                    "View featured items",
                    "Add items to order",
                    "Navigate to other sections"
                ]
            },
            "transition_description": "After scrolling, the page transitioned to display featured items from Chipotle Mexican Grill, showcasing the most liked options along with their prices, while details like location and operational hours remained visible."
        },
        {
            "before_state_description": {
                "website": "Uber Eats",
                "overview": "The Uber Eats page for Chipotle Mexican Grill displays featured items available for delivery, along with the restaurant's details and menu categories.",
                "functional_analysis": "This page allows users to view and order food from Chipotle Mexican Grill, showcasing featured items with pricing and popularity ratings.",
                "functional_actions": [
                    "Order food",
                    "View menu categories",
                    "Add items to cart"
                ]
            },
            "after_state_description": {
                "website": "Uber Eats",
                "overview": "A detailed view of the Burrito Bowl item selected from the featured items on the Chipotle Mexican Grill Uber Eats page.",
                "functional_analysis": "This view provides additional information about the Burrito Bowl, including customization options for ingredients and pricing.",
                "functional_actions": [
                    "Customize Burrito Bowl",
                    "Add to cart",
                    "Go back to menu"
                ]
            },
            "transition_description": "After clicking on the 'most liked' item, the page transitioned to a detailed view of the Burrito Bowl, displaying its price, description, and options for customization."
        },
        {
            "before_state_description": {
                "website": "Uber Eats",
                "overview": "The page displays the menu for Chipotle Mexican Grill, showcasing a specific item, the Burrito Bowl, along with its details.",
                "functional_analysis": "This page is used to view menu items from Chipotle Mexican Grill, select preferences, and order food for delivery.",
                "functional_actions": [
                    "Choose protein or veggie",
                    "View item details",
                    "Close the item details"
                ]
            },
            "after_state_description": {
                "website": "Uber Eats",
                "overview": "The page now displays the main menu for Chipotle Mexican Grill with featured items and their prices.",
                "functional_analysis": "The main menu is available for browsing different food options, including featured items and their descriptions.",
                "functional_actions": [
                    "Select an item to view details",
                    "Add items to cart",
                    "Browse more menu options"
                ]
            },
            "transition_description": "The action of closing the item details resulted in the page transitioning from a focused view on the Burrito Bowl to displaying the full menu of featured items from Chipotle Mexican Grill."
        },
        {
            "before_state_description": {
                "website": "Uber Eats",
                "overview": "The page features a restaurant offering delivery services, showcasing a selection of featured items and their prices.",
                "functional_analysis": "Users can view featured menu items, their prices, and ratings, as well as browse the menu in various sections.",
                "functional_actions": [
                    "View featured items",
                    "Add items to cart",
                    "Browse menu categories"
                ]
            },
            "after_state_description": {
                "website": "Uber Eats",
                "overview": "A detailed view of the selected menu item, which includes a description, price, and customization options.",
                "functional_analysis": "Users can see detailed information about the selected menu item, including description, pricing, and customization choices.",
                "functional_actions": [
                    "Select item options",
                    "Add item to cart",
                    "View nutritional information"
                ]
            },
            "transition_description": "Upon clicking the '2nd most liked' item, a detail overlay for the Burrito appears, displaying its description, price, and customization options."
        },
        {
            "before_state_description": {
                "website": "Uber Eats",
                "overview": "The page displays menu items for Chipotle Mexican Grill, emphasizing a specific burrito selection.",
                "functional_analysis": "The page is used to browse food items available for delivery from Chipotle Mexican Grill, allowing users to view details, prices, and options for customization of food items.",
                "functional_actions": [
                    "View item details",
                    "Add items to cart",
                    "Select customizable options"
                ]
            },
            "after_state_description": {
                "website": "Uber Eats",
                "overview": "After clicking, the page displays the updated featured items section, including the burrito and other menu offerings.",
                "functional_analysis": "The page now prominently features the listed menu items, showcasing their popularity and reviews alongside updated information about the restaurant.",
                "functional_actions": [
                    "View item details",
                    "Add items to cart",
                    "Select customizable options"
                ]
            },
            "transition_description": "The action of clicking resulted in the main view updating to display a new arrangement of featured items, highlighting their popularity and the ratings associated with each item."
        },
        {
            "before_state_description": {
                "website": "Uber Eats",
                "overview": "The page features items available for delivery from Chipotle Mexican Grill, showing a list of popular choices with their prices and ratings.",
                "functional_analysis": "The page primarily allows users to view and order food items from a restaurant, focusing on featured items at Chipotle.",
                "functional_actions": [
                    "Add item to cart",
                    "View item details"
                ]
            },
            "after_state_description": {
                "website": "Uber Eats",
                "overview": "A detailed popup view of the Quesadilla item from Chipotle Mexican Grill is displayed, including its description and options for customization.",
                "functional_analysis": "The page now allows users to see detailed information about a specific item, including customization options for the Quesadilla.",
                "functional_actions": [
                    "Select protein or veggie",
                    "Add to cart",
                    "Close popup"
                ]
            },
            "transition_description": "After clicking on the '#3 most liked' Quesadilla item, a detailed view opens, showing its description, price, and customization options, replacing the static listing of featured items."
        },
        {
            "before_state_description": {
                "website": "Uber Eats",
                "overview": "The page displays a food item from Chipotle Mexican Grill, specifically a Quesadilla priced at $14.35 with various options for protein or veggie choices.",
                "functional_analysis": "This page allows users to view the details of the food item they are interested in, along with options for customization (choices for protein or veggies).",
                "functional_actions": [
                    "View item details",
                    "Select protein or veggie",
                    "Add item to cart"
                ]
            },
            "after_state_description": {
                "website": "Uber Eats",
                "overview": "The page remains focused on the Quesadilla item from Chipotle Mexican Grill, with the same pricing and customization options available.",
                "functional_analysis": "The functionality of the page remains unchanged, allowing continued interaction with the food item and its customization options.",
                "functional_actions": [
                    "View item details",
                    "Select protein or veggie",
                    "Add item to cart"
                ]
            },
            "transition_description": "No visible changes occurred on the page after the click action."
        }
    ]
}
