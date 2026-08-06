import streamlit as st

RECIPE_DB = [
    {
        "name": "Quick Garlic Butter Pasta",
        "ingredients": ["pasta", "garlic", "butter"],
        "budget": "low",
        "time": 15,
        "instructions": "Boil pasta. Saute minced garlic in butter. Toss together with salt and pepper."
    },
    {
        "name": "Classic Grilled Cheese",
        "ingredients": ["bread", "cheese", "butter"],
        "budget": "Low",
        "time": 10,
        "instructions": "Butter bread slices. Place cheese in between. Toast on a skillet until golden brown."
    },
    {
        "name": "Loaded Veggie Omelet",
        "ingredients": ["eggs", "cheese", "onion", "pepper", "tomato"],
        "budget": "Low",
        "time": 25,
        "instructions": "Whisk eggs. Pour into a hot skillet. Add chopped vegetables and cheese. Fold in half."
    },
    {
        "name": "Budget Beef Chili",
        "ingredients": ["ground beef", "beans", "tomato", "onion"],
        "budget": "Medium",
        "time": 40,
        "instructions": "Brown beef with onion. Stir in beans and crushed tomatoes. Simmer on low heat."
    },
    {
         "name": "Stir-Fry Chicken & Rice",
         "ingredients": ["Chicken", "rice", "onion", "soy sauce", "garlic"],
         "budget": "Medium",
         "time": 25,
         "instructions": "cook rice. Saute chicken and onion in a pan. Add garlic and sou sauce. Serve over rice."
    },
    {
         "name": "Pan-Seared Steak with Garlic Butter",
         "ingredients": ["Steak", "garlic", "butter"],
         "budget": "High",
         "time": 20,
         "instructions": "Season steak with salt/pepper. Sear in  screaminghot skillet. Baste with garlic butter."
    }
]

st.set_page_config(page_title="MealMatch", page_icon=" ", layout="centered")
st. title("MealMatch App")
st.subheader("Your smart, minimal ingredients meal matching assistant.")
st.write("Find straightforward meal ideas based on what you have right now.")

st. divider()

st.markdown("### Step 1: What's in your kitchen?")
all_available_ingredients = sorted(list(set(int for recipe in RECIPE_DB for ing in recipe["ingredients"])))
user_ingredients = st.multiselect(
    "Select the ingredients you have on hand:",
    options=all_available_ingredients,
    placeholder="e.g., garlic, cheese, butter"
)

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Step 2: Set Budget")
    user_budget = st.selectbox(
        "Select your budget tier:",
        options=["Low", "Medium", "High"],
        index=0
    )

with col2:
    st.markdown("### clock Step 3: Cooking Time")
    user_time = st.slider(
        "Maximum perparation time (minutes):",
        min_value=5,
        max_value=60,
        value=30,
        step=5
    )

st.divider()

if st.button("Match My Meal", type="primary"):
    if not user_ingredients:
        st.warning("Please select at least one ingredient to get started.")
    else:
        st.markdown("### Tailored Suggestions")

        matches = []
        for recipe in RECIPE_DB:
            if recipe["budget"] != user_budget:
                continue

            if recipe["time"] > user_time:
                continue

            matching_ings = [ing for ing in recipe["ingredients"] if ing in user_ingredients]

            if matching_ings:
                match_percentage = len(matching_ings) / len(recipe["ingredients"])
                matches.append((recipe, match_percentage, matching_ings))

        matches.sort(key=lambda x: x[1], reverse=True)

        final_suggestions = matches[:3]

        if final_suggestions:
            st.success(f"Found {len(final_suggestions)} straightforward meal idea(s) for you!")

            for idx, (recipe, score, matched) in enumerate(final_suggestions):
                with st.expander(f" {recipe['name']} ({recipe['time']} mins x {recipe['budget']} Budget)"):
                    st. write(f"**Matched Ingredients:** {', '.join(matched)}")
                    
                    missing_ingredients = [i for i in recipe["ingredients"] if i not in user_ingredients]
                    if missing_ingredients:
                        st.write(f" **Missing items:** {', '.join(missing_ingredients)}")
                    else:
                        st.write("You have 100% of the core ingredients!")

                        st.write("**Instructions:**")
                        st.write(recipe["instructions"])
            else:
                st.info("No perfect matches found. Try selecting more ingredients, raising your budget, or expanding cooking time parameters.")

                