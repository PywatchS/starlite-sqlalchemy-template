import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.apps.decks import models
from tests.decks.conftest import another_card_data, card_data


@pytest.mark.asyncio
def test_get_cards_empty(client: TestClient, deck: models.Deck):
    response = client.get(f"/api/decks/{deck.id}/cards/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["items"]) == 0

    response = client.get(f"/api/decks/{deck.id}/cards/0/")
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
def test_get_cards(client: TestClient, card: models.Card):
    response = client.get(f"/api/decks/{card.deck_id}/cards/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["items"]) == 1
    for k, v in data["items"][0].items():
        assert v == getattr(card, k)


@pytest.mark.asyncio
def test_get_card(client: TestClient, card: models.Card):
    response = client.get(f"/api/cards/{card.id}/")
    assert response.status_code == status.HTTP_200_OK
    for k, v in response.json().items():
        assert v == getattr(card, k)


@pytest.mark.asyncio
def test_create_cards(client: TestClient, deck: models.Deck):
    # bulk create
    response = client.post(
        f"/api/decks/{deck.id}/cards/",
        json=[card_data.dict(), another_card_data.dict()],
    )
    assert response.status_code == status.HTTP_200_OK
    created_data = response.json()

    # check creation
    response = client.get(f"/api/decks/{deck.id}/cards/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert created_data == data
    assert len(data["items"]) == 2
    for k, v in card_data.dict().items():
        assert data["items"][0][k] == v
    for k, v in another_card_data.dict().items():
        assert data["items"][1][k] == v

    # unique constraint error
    response = client.post(
        f"/api/decks/{deck.id}/cards/",
        json=[card_data.dict(), another_card_data.dict()],
    )
    data = response.json()
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert data["detail"][0]["msg"] == "Unique constraint violated for Card"
    assert data["detail"][0]["loc"] == ["deck_id, front"]


@pytest.mark.asyncio
def test_update_cards(
    client: TestClient,
    deck: models.Deck,
    card: models.Card,
    another_card: models.Card,
):
    updated_data = [
        {
            "id": card.id,
            "front": "card front updated",
            "back": "card back updated",
            "hint": "card hint updated",
        },
        {
            "id": another_card.id,
            "front": "card front2 updated",
            "back": "card back2 updated",
            "hint": "card hint2 updated",
        },
    ]
    response = client.put(
        f"/api/decks/{deck.id}/cards/",
        json=updated_data,
    )
    assert response.status_code == status.HTTP_200_OK
    cards = response.json()["items"]
    for x in cards:
        assert x.pop("deck_id") == deck.id
    assert cards == updated_data

    # check creation
    response = client.get(f"/api/decks/{deck.id}/cards/")
    assert response.status_code == status.HTTP_200_OK
    cards = response.json()["items"]
    assert len(cards) == 2
    for x in cards:
        assert x.pop("deck_id") == deck.id
    assert cards == updated_data