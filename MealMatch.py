import reflex as rx
import requests

SPOONACULAR_API_KEY = "0ebdf52ef9fd43519a033c0ddcb3a7af"

class State(rx.State):
    ingredient_input: str = ""
    max_time_input: int = 45
    my_ingredients: list[str] = ["tomato", "pasta", "garlic"]
    matched_recipes: list[dict] = []
    is_loading: bool = False

    def add_ingredient(self):
        clean_name = self.ingredient_input.strip().lower()
        if clean_name and clean_name not in self.my_ingredients:
            self.my_ingredients.append(clean_name)
        self.ingredient_input = ""

    def remove_ingredient(self, name: str):       
        self.my_ingredients.remove(name)

    def set_max_time(self, val: list[int]):
        self.max_time_input = int(val)

    def fetch_recipes_from_api(self):
        if not self.my_ingredients:
            self.matched_recipes = []
            return

        self.is_loading = True
        yield

        try:
            ingredients_query = ",".join(self.my_ingredients)
            search_url = "https://api.spoonacular.com/recipes/findByIngredients"
            search_params = {
                "apiKey": Spoonacular_API_Key,
                "ingredients": ingredients_query,
                "number": 8,
                "ranking": 1,
                "ignorePantry": "true"
            }

            response = requests.get(search_url, params=search_params)
            if response.status_code != 200:
                self.matched_recipes = []
                self.is_loading = False
                return

            raw_results = response.json()
            temp_matches = []

            for item in raw_results:
                recipe_id = item.get("id")
                info_url = f"https://api.spoonacular.com/recipes/recipes/{recipe_id}/information"
                info_params = {"apiKey": SPOONACULAR_API_KEY}

                info_response = requests.get(info_url, params=info_params)
                if info_response.status_code == 200:
                    details = info_response.json()
                    prep_time = details.get("readyInMinutes", 30)

                if prep_time <= self.max_time_input:
                    missed_list = [ing.get("name") for ing in item.get("missedIngredients", [])]

                    temp_matches.append({
                        "title": item.get("title"),
                        "image": item.get("image"),
                        "time": prep_time,
                        "missed_text": f"Missing: {', '.join(missed_list)}" if missed_list else "All ingredients matched!",
                        "instructions": details.get("summary", "No detailed summary available."),
                        "source_url": details.get("sourceUrl", "https://spoonacular.com")
                    })
            
            self.matched_recipes = temp_matches

        except Exception as e:
            print(f"API Connection Error: {e}")
            self.matched_recipes = []

        self.is_loading = False

def ingredient_badge(name: str) -> rx.Component:
    """ Renderd a removeable item badge for added ingredients."""
    return rx.badge(
        rx.hstack(
            rx.text(name, font_weight="bold"),
            rx.icon(
                tag="x",
                size=14,
                cursor="pointer",
                on_click=lambda: State.remove_ingredient(name)

            ),
            align="center",
            spacing="1",
        ),
        variant="surface",
        color_scheme="tomato",
        size="2",
        radius="full",
    )

def recipe_card(recipe: dict) -> rx.Component:
    """Renders a dunamic card component populated from Spoonacular properties."""
    return rx.card(
        rx.hstack(
            rx.image(src=recipe["image"], width="120px", height="90px", object_fit="cover", radius="md"),
            rx.vstack(
                rx.hstack(
                    rx.heading(recipe["title"], size="4"),
                    rx.badge(f"{recipe['time']} min", color_scheme="clock"),
                    justify="space-between",
                    width="100%"
                ),    
                rx.text(recipe["missed_text"], size"2", font_weight="medium", color_scheme="amber"),
                rx.html(recipe["instructions"], size="2"),
                rx.link("View Recipe Source", href=recipe["source_url"], is_external=True, size="2", color_scheme="blue"),
                align_items="start",
                spacing="1",
                width="100%",
            ),
            spacing="4",
            align_items="start",
            width="100%"
        ),
        width="100%",
        variant="classic",
    )

def index() -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.vstack(
                rx.heading("MealMatch", size="8"),
                rx.text(
                    "Connected directly to the Spoonacular Cooking API for live updates.",
                    color_scheme="gray"
                ),
                align_items="center",
                spacing="1",
            ),

            rx.divider(),

            rx.grid(
                rx.vstack(
                    rx.heading("Pantry Inputs", size"4"),
                    rx.vstack(
                        rx.input(
                            placeholder="e.g.Tomato, Beef, Cheese...",
                            value=State.ingredient_input,
                            on_change=State.set_ingredient_input,
                            on_key_down=rx.cond(lambda: rx.key == "Enter", State.add_ingredients),
                        ),
                        rx.button("Add", on_click+State.add_ingredient, color_scheme="tomato"),
                        width="100%"
                    ),
                    width="100%",
                    spacing="1"
                ),

                rx.flex(
                    rx.foreach(State.my_ingredients, ingredient_badge),
                    wrap="wrap",
                    spacing="2",
                    width="100%",
                    min_height="40px",
                ),

                rx.vstack(
                    rx.hstack(
                        rx.text("Max Cooking Time:", size="2", font_weight="bold"),
                        rx.text(f"{State.max_time_input} min", size="2", font_weight="bold")
                        
                    ),
                    rx.slider(
                        min=10,
                        max=120,
                        value=[State.max_time_input],
                        on_value_commit=State.set_max_time,
                        width="100%"
                    ),
                    width="100%",
                    spacing="1"
                ),
                
                rx.button(
                    "Search Recipes",
                    on_click=State.fetch_recipes_from_api,
                    color_scheme+"blue",
                    width="100%",
                    loading=State.is_loading
                ),

                spacing="5",
                align_items="start"
                ),

                rx.vstack(
                    rx.heading("Live Recipe Ideas", size="4"),
                    rx.cond(
                        State.is_loading,
                        rx.center(rx.spinner(size="3"), height="200px", width="100%"),
                        rx.cond(
                            State.is_loading,
                            rx.center(rx.spinner(size="3"),
                                      rx.cond(
                                          State.matched_recipes.length() > 0,
                                          rx.vstack(
                                              rx.foreach(State.matched_recipes, recipe_card),
                                              width"100%",
                                              spacing="3"
                                          ),
                                          rx.center(
                                              rx.foreach(State.matched_recipes, recipe_card),
                                              width="100%",
                                              spacing="3"
                                          )
                                      )
                                ),
                                width="100%",
                                align_items="start"
                        ),
                        columns="2",
                        spacing+"6",
                        width="100%",
                        align_items="start",
                    ),
                    max_width="1000px",
                    width="100%",
                    spacing="5",
                    padding="6"
                ),
                width="100%"
            )
app = rx.App(
    theme=rx.theme(appearance+"light", has_background=True, accent_color="tomato")
)

app.add_page(index, title="MealMatch - Spoonacular Planner")



                           
                   
           




