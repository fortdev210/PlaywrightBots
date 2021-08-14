class Supplier:
    WALMART_CODE = 'W'
    HOMEDEPOT_CODE = 'P'

    WALMART_SELLER_ID = 'F55CDC31AB754BB68FE0B39041159D63'
    WALMART_GROCERY_API = "https://www.walmart.com/grocery/v4/api/products/browse?count=60&offset=0&page=1&storeId=2086"
    WALMART_SEARCH_API = "https://www.walmart.com/search/api/preso?page=1&cat_id={cat_id}&prg=desktop&facet=retailer:Walmart.com"
    WALMART_SEARCH_SHELF_ID_API = "https://www.walmart.com/search/api/preso?page=1&cat_id=0&_be_shelf_id={_be_shelf_id}&prg=desktop&facet=shelf_id:{_be_shelf_id}||retailer:Walmart.com"
