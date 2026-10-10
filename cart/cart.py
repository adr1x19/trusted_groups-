# cart/cart.py
from dataclasses import dataclass, field
from cart.groceryItem import cartItem, groceryItem
from enum import Enum
import time

import asyncio

class cartStatus(Enum):
    OPEN = 1
    LOCKED = 2
    EXPIRED = 3 

@dataclass
class cart:
    cartID: str
    hostEmail: str
    timer: int = 3600  # Duration in seconds
    status: cartStatus = cartStatus.OPEN
    participants: dict[str, str] = field(default_factory=dict)
    userItems: dict[str, dict[str, cartItem]] = field(default_factory=dict)
    
    # Store the exact time the cart was created (Unix timestamp)
    createdAt: float = field(default_factory=time.time)

    # Helper method to dynamically check if the timer is up
    def isExpired(self) -> bool:
        return time.time() > (self.createdAt + self.timer)

    # Helper method to get the true status right now
    def getCurrentStatus(self) -> cartStatus:
        if self.status == cartStatus.LOCKED:
            return cartStatus.LOCKED
        if self.isExpired():
            return cartStatus.EXPIRED
        return cartStatus.OPEN