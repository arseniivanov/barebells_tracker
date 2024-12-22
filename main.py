from barebells_tracker.tracker import create_default_tracker

def main():
    # Create tracker with all scrapers
    tracker = create_default_tracker()
    tracker.add_exclusion_pattern('chewy')
    
    # Run all scrapers
    tracker.run()
    
    # Print store summary
    print("\nProducts found by store:")
    for store, count in tracker.get_store_summary().items():
        print(f"{store}: {count} products")
    
    # Print best deals for single bars
    print("\nBest deals for single bars:")
    for product in tracker.get_best_deals(package_size=None, limit=7):
        print(f"- {product.name} at {product.price:.2f} SEK from {product.store}")
        print(f"- {product.url}")
    
    # Print best deals for 12-packs
    print("\nBest deals for 12-packs:")
    for product in tracker.get_best_deals(package_size=12, limit=7):
        print(f"- {product.name}")
        print(f"  Total price: {product.price:.2f} SEK")
        print(f"  Price per bar: {product.per_unit_price:.2f} SEK")
        print(f"  Store: {product.store}")
        print(f"- {product.url}")
    
    # Print price ranges
    singles_range = tracker.get_price_range(package_size=None)
    multi_range = tracker.get_price_range(package_size=12)
    
    print("\nPrice ranges:")
    print("Single bars:")
    print(f"- Min: {singles_range['min_price']:.2f} SEK")
    print(f"- Max: {singles_range['max_price']:.2f} SEK")
    print(f"- Avg: {singles_range['avg_price']:.2f} SEK")
    
    print("\n12-packs:")
    print(f"- Min: {multi_range['min_price']:.2f} SEK")
    print(f"- Max: {multi_range['max_price']:.2f} SEK")
    print(f"- Avg: {multi_range['avg_price']:.2f} SEK")

if __name__ == "__main__":
    main()
