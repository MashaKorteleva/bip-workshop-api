"""
She Builds Products — Workshop API
A tiny food-delivery API used as the hands-on sandbox.

Swagger playground is auto-generated at  /docs
"""

from fastapi import FastAPI, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field
from typing import Optional, Literal
from copy import deepcopy

# ----------------------------------------------------------------------------
# CONFIG
# ----------------------------------------------------------------------------

API_KEY = "sbp-workshop-2026"          # <- the key you put on the slide
PROTECTED_ID_LIMIT = 100                # seeded orders (id <= 100) can't be changed/deleted
NEXT_NEW_ID = 1000                      # orders created by attendees start here

app = FastAPI(
    title="She Builds Products — Food Delivery API",
    description=(
        "A small, friendly API to practise on.\n\n"
        "**How to use this page**\n\n"
        "1. Click the green **Authorize** button, top right.\n"
        "2. Paste the API key you were given, and click Authorize.\n"
        "3. Pick an endpoint below, click **Try it out**, then **Execute**.\n\n"
        "Everything you create here disappears when the API restarts. "
        "Break whatever you like."
    ),
    version="1.0.0",
)

# ----------------------------------------------------------------------------
# AUTH  — a single key, sent on EVERY request (rule 3: the API has no memory)
# ----------------------------------------------------------------------------

api_key_header = APIKeyHeader(
    name="X-API-Key",
    description="Your workshop API key.",
    auto_error=False,
)


def check_key(key: Optional[str] = Security(api_key_header)) -> str:
    if key is None:
        raise HTTPException(
            status_code=401,
            detail="No API key. Click Authorize at the top of this page and paste your key.",
        )
    if key != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="That API key isn't right. Check for stray spaces.",
        )
    return key


# ----------------------------------------------------------------------------
# MODELS
# ----------------------------------------------------------------------------

Status = Literal["preparing", "on_the_way", "delivered", "cancelled"]
City = Literal["frankfurt", "berlin", "munich"]


class Order(BaseModel):
    id: int
    customer: str
    restaurant: str
    city: City
    items: list[str]
    total_eur: float
    status: Status
    driver_id: Optional[int] = None


class NewOrder(BaseModel):
    customer: str = Field(..., examples=["Masha"])
    restaurant: str = Field(..., examples=["Pizza Napoli"])
    city: City = Field(..., examples=["frankfurt"])
    items: list[str] = Field(..., examples=[["Margherita", "Tiramisu"]])
    total_eur: float = Field(..., examples=[18.50])


class StatusUpdate(BaseModel):
    status: Status = Field(..., examples=["on_the_way"])


class Driver(BaseModel):
    id: int
    name: str
    city: City
    vehicle: str
    lat: float
    lng: float


class Restaurant(BaseModel):
    id: int
    name: str
    city: City
    cuisine: str
    open_now: bool


# ----------------------------------------------------------------------------
# SEED DATA  — the bedrock. Predictable, so the exercises always work.
# ----------------------------------------------------------------------------

SEED_ORDERS: list[dict] = [
    # --- FRANKFURT (8) ---
    {"id": 1,  "customer": "Anna",    "restaurant": "Pizza Napoli",   "city": "frankfurt", "items": ["Margherita", "Coke"],          "total_eur": 14.50, "status": "delivered",  "driver_id": 87},
    {"id": 2,  "customer": "Ben",     "restaurant": "Sushi Zen",      "city": "frankfurt", "items": ["Salmon set"],                  "total_eur": 22.00, "status": "delivered",  "driver_id": 87},
    {"id": 3,  "customer": "Clara",   "restaurant": "Curry Haus",     "city": "frankfurt", "items": ["Butter chicken", "Naan"],      "total_eur": 19.90, "status": "on_the_way", "driver_id": 88},
    {"id": 4,  "customer": "Dmitri",  "restaurant": "Pizza Napoli",   "city": "frankfurt", "items": ["Quattro Formaggi"],            "total_eur": 16.00, "status": "on_the_way", "driver_id": 87},
    {"id": 5,  "customer": "Elena",   "restaurant": "Green Bowl",     "city": "frankfurt", "items": ["Falafel bowl"],                "total_eur": 11.50, "status": "preparing",  "driver_id": None},
    {"id": 6,  "customer": "Farid",   "restaurant": "Sushi Zen",      "city": "frankfurt", "items": ["Tuna nigiri", "Miso soup"],    "total_eur": 27.40, "status": "delivered",  "driver_id": 88},
    {"id": 7,  "customer": "Greta",   "restaurant": "Curry Haus",     "city": "frankfurt", "items": ["Vegetable korma"],             "total_eur": 15.00, "status": "cancelled",  "driver_id": None},
    {"id": 8,  "customer": "Hugo",    "restaurant": "Green Bowl",     "city": "frankfurt", "items": ["Poke bowl", "Matcha"],         "total_eur": 18.20, "status": "delivered",  "driver_id": 87},

    # --- BERLIN (7) ---
    {"id": 9,  "customer": "Ines",    "restaurant": "Doner Palace",   "city": "berlin",    "items": ["Doner", "Ayran"],              "total_eur": 9.50,  "status": "delivered",  "driver_id": 91},
    {"id": 10, "customer": "Jonas",   "restaurant": "Pho Corner",     "city": "berlin",    "items": ["Pho bo"],                      "total_eur": 13.00, "status": "on_the_way", "driver_id": 91},
    {"id": 11, "customer": "Kata",    "restaurant": "Burger Bros",    "city": "berlin",    "items": ["Cheeseburger", "Fries"],       "total_eur": 16.80, "status": "preparing",  "driver_id": None},
    {"id": 12, "customer": "Lukas",   "restaurant": "Doner Palace",   "city": "berlin",    "items": ["Halloumi wrap"],               "total_eur": 8.90,  "status": "delivered",  "driver_id": 92},
    {"id": 13, "customer": "Mira",    "restaurant": "Pho Corner",     "city": "berlin",    "items": ["Summer rolls", "Bun cha"],     "total_eur": 21.30, "status": "on_the_way", "driver_id": 92},
    {"id": 14, "customer": "Noah",    "restaurant": "Burger Bros",    "city": "berlin",    "items": ["Double bacon"],                "total_eur": 19.00, "status": "preparing",  "driver_id": None},
    {"id": 15, "customer": "Olga",    "restaurant": "Burger Bros",    "city": "berlin",    "items": ["Veggie burger"],               "total_eur": 14.00, "status": "cancelled",  "driver_id": None},

    # --- MUNICH (5) ---
    {"id": 16, "customer": "Pia",     "restaurant": "Brezel Bar",     "city": "munich",    "items": ["Pretzel", "Weissbier"],        "total_eur": 12.00, "status": "delivered",  "driver_id": 95},
    {"id": 17, "customer": "Quinn",   "restaurant": "Taco Loco",      "city": "munich",    "items": ["Tacos al pastor"],             "total_eur": 17.50, "status": "on_the_way", "driver_id": 95},
    {"id": 18, "customer": "Rosa",    "restaurant": "Brezel Bar",     "city": "munich",    "items": ["Obatzda", "Pretzel"],          "total_eur": 13.60, "status": "delivered",  "driver_id": 96},
    {"id": 19, "customer": "Samir",   "restaurant": "Taco Loco",      "city": "munich",    "items": ["Burrito", "Guacamole"],        "total_eur": 20.10, "status": "preparing",  "driver_id": None},
    {"id": 20, "customer": "Tessa",   "restaurant": "Noodle House",   "city": "munich",    "items": ["Pad thai"],                    "total_eur": 15.40, "status": "delivered",  "driver_id": 96},
]

SEED_DRIVERS: list[dict] = [
    {"id": 87, "name": "Marco",  "city": "frankfurt", "vehicle": "scooter", "lat": 50.1109, "lng": 8.6821},
    {"id": 88, "name": "Sofia",  "city": "frankfurt", "vehicle": "bicycle", "lat": 50.1155, "lng": 8.6842},
    {"id": 91, "name": "Tomas",  "city": "berlin",    "vehicle": "scooter", "lat": 52.5200, "lng": 13.4050},
    {"id": 92, "name": "Yara",   "city": "berlin",    "vehicle": "car",     "lat": 52.5163, "lng": 13.3777},
    {"id": 95, "name": "Leon",   "city": "munich",    "vehicle": "bicycle", "lat": 48.1372, "lng": 11.5755},
    {"id": 96, "name": "Nadia",  "city": "munich",    "vehicle": "scooter", "lat": 48.1391, "lng": 11.5802},
]

SEED_RESTAURANTS: list[dict] = [
    {"id": 1, "name": "Pizza Napoli",  "city": "frankfurt", "cuisine": "italian",   "open_now": True},
    {"id": 2, "name": "Sushi Zen",     "city": "frankfurt", "cuisine": "japanese",  "open_now": True},
    {"id": 3, "name": "Curry Haus",    "city": "frankfurt", "cuisine": "indian",    "open_now": False},
    {"id": 4, "name": "Green Bowl",    "city": "frankfurt", "cuisine": "healthy",   "open_now": True},
    {"id": 5, "name": "Doner Palace",  "city": "berlin",    "cuisine": "turkish",   "open_now": True},
    {"id": 6, "name": "Pho Corner",    "city": "berlin",    "cuisine": "vietnamese","open_now": True},
    {"id": 7, "name": "Burger Bros",   "city": "berlin",    "cuisine": "american",  "open_now": False},
    {"id": 8, "name": "Brezel Bar",    "city": "munich",    "cuisine": "german",    "open_now": True},
    {"id": 9, "name": "Taco Loco",     "city": "munich",    "cuisine": "mexican",   "open_now": True},
    {"id": 10,"name": "Noodle House",  "city": "munich",    "cuisine": "thai",      "open_now": True},
]

# live, mutable state
orders: dict[int, dict] = {}
next_id: int = NEXT_NEW_ID


def load_seed() -> None:
    global orders, next_id
    orders = {o["id"]: deepcopy(o) for o in SEED_ORDERS}
    next_id = NEXT_NEW_ID


load_seed()


# ----------------------------------------------------------------------------
# ORDERS
# ----------------------------------------------------------------------------

@app.get("/orders", response_model=list[Order], tags=["Orders"],
         summary="Get all orders")
def list_orders(
    status: Optional[Status] = None,
    city: Optional[City] = None,
    _key: str = Security(check_key),
):
    """
    Returns every order.

    Add **parameters** to narrow it down — try `status=delivered`,
    or `city=frankfurt`, or both together.
    """
    result = list(orders.values())
    if status:
        result = [o for o in result if o["status"] == status]
    if city:
        result = [o for o in result if o["city"] == city]
    return sorted(result, key=lambda o: o["id"])


@app.get("/orders/{order_id}", response_model=Order, tags=["Orders"],
         summary="Get one order")
def get_order(order_id: int, _key: str = Security(check_key)):
    """Give me *this* order. Try `3`. Then try `999` and see what happens."""
    if order_id not in orders:
        raise HTTPException(status_code=404, detail=f"No order with id {order_id}.")
    return orders[order_id]


@app.post("/orders", response_model=Order, status_code=201, tags=["Orders"],
          summary="Place a new order")
def create_order(new: NewOrder, _key: str = Security(check_key)):
    """
    Creates an order. Note the response code: **201 Created**, not 200.

    Your new order gets an id from 1000 upwards — it's yours, do what you like with it.
    """
    global next_id
    order = {
        "id": next_id,
        **new.model_dump(),
        "status": "preparing",
        "driver_id": None,
    }
    orders[next_id] = order
    next_id += 1
    return order


@app.patch("/orders/{order_id}", response_model=Order, tags=["Orders"],
           summary="Update an order's status")
def update_status(order_id: int, update: StatusUpdate, _key: str = Security(check_key)):
    """
    Move an order along: `preparing` -> `on_the_way` -> `delivered`.

    The 20 seeded orders are read-only — try changing one and see what the API says.
    """
    if order_id not in orders:
        raise HTTPException(status_code=404, detail=f"No order with id {order_id}.")
    if order_id <= PROTECTED_ID_LIMIT:
        raise HTTPException(
            status_code=403,
            detail="This is a seeded order and can't be changed — everyone in the workshop shares it. Create your own with POST /orders and edit that instead.",
        )
    orders[order_id]["status"] = update.status
    return orders[order_id]


@app.delete("/orders/{order_id}", status_code=204, tags=["Orders"],
            summary="Cancel an order")
def delete_order(order_id: int, _key: str = Security(check_key)):
    """
    Deletes an order. Note the response: **204 No Content** — it worked,
    and there is nothing to give back.
    """
    if order_id not in orders:
        raise HTTPException(status_code=404, detail=f"No order with id {order_id}.")
    if order_id <= PROTECTED_ID_LIMIT:
        raise HTTPException(
            status_code=403,
            detail="This is a seeded order and can't be deleted — everyone in the workshop shares it. Create your own with POST /orders and delete that instead.",
        )
    del orders[order_id]
    return None


# ----------------------------------------------------------------------------
# DRIVERS  &  RESTAURANTS
# ----------------------------------------------------------------------------

@app.get("/drivers/{driver_id}", response_model=Driver, tags=["Drivers"],
         summary="Where is the driver?")
def get_driver(driver_id: int, _key: str = Security(check_key)):
    """This is the dot on the map. Try driver `87` — he's the one on the scooter."""
    for d in SEED_DRIVERS:
        if d["id"] == driver_id:
            return d
    raise HTTPException(status_code=404, detail=f"No driver with id {driver_id}.")


@app.get("/restaurants", response_model=list[Restaurant], tags=["Restaurants"],
         summary="Get all restaurants")
def list_restaurants(
    city: Optional[City] = None,
    open_now: Optional[bool] = None,
    _key: str = Security(check_key),
):
    """Try `city=berlin`, or `open_now=true`, or both."""
    result = SEED_RESTAURANTS
    if city:
        result = [r for r in result if r["city"] == city]
    if open_now is not None:
        result = [r for r in result if r["open_now"] == open_now]
    return result


# ----------------------------------------------------------------------------
# RESET  — your panic button
# ----------------------------------------------------------------------------

@app.post("/reset", tags=["Workshop"], summary="Reset everything back to the seed data")
def reset(_key: str = Security(check_key)):
    """Wipes anything created during the session and restores the original 20 orders."""
    load_seed()
    return {"message": "Reset done.", "orders": len(orders)}
