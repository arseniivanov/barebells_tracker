# 🍫 Barebells Price Tracker

Let's face it - Barebells makes the best protein bars out there, and I'll fight anyone who says otherwise.

BUT, these heavenly bars of protein-packed goodness aren't exactly cheap. Dropping 25-30 SEK on a single bar feels like a personal attack on my wallet. And don't even get me started on how Prisjakt and Pricerunner are about as reliable as a chocolate teapot when it comes to Barebells prices - showing prices from three months ago or from stores that haven't had stock since the stone age.

That's where this beauty comes in. This tracker scrapes real-time prices from actual stores in Sweden, so you can find those sweet, sweet deals without having to check 12 different websites manually like some kind of digital coupon hunter from the 90s.

## Features

- Real-time price tracking across major Swedish retailers
- Can filter out those sus "chewy" and "soft" variants (protein/calorie bro)
- Shows both single bar prices and multipack deals
- Actually tells you if stuff is in stock
- Helps you dodge the "fake" discount prices that some sneaky stores try to pull

## Installation
Linux only

First, get yourself pixi

```bash
curl -fsSL https://pixi.sh/install.sh | bash
```

Then just do:

```bash
pixi install
```

## Running the Tracker

Jump into the pixi shell:
```bash
pixi shell
```

And let it rip:
```bash
python main.py
```

Boom! Now you can find those protein bars at prices that won't make your bank account cry.

## Disclaimer

This project was created out of pure love for Barebells protein bars and a strong dislike for overpaying for them. No retailers were harmed in the making of this tracker.

