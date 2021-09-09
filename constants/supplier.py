class Supplier:
    WALMART_CODE = 'W'
    HOMEDEPOT_CODE = 'P'

    WALMART_SELLER_ID = 'F55CDC31AB754BB68FE0B39041159D63'
    WALMART_GROCERY_API = "https://www.walmart.com/grocery/v4/api/products/browse?count=60&offset=0&page=1&storeId=2086"
    WALMART_SEARCH_API = "https://www.walmart.com/search/api/preso?page=1&cat_id={cat_id}&prg=desktop&facet=retailer:Walmart.com"
    WALMART_SEARCH_SHELF_ID_API = "https://www.walmart.com/search/api/preso?page=1&cat_id=0&_be_shelf_id={_be_shelf_id}&prg=desktop&facet=shelf_id:{_be_shelf_id}||retailer:Walmart.com"
    WALMART_BASE_URL = 'https://www.walmart.com'
    WALMART_BASE_BROWSER_URL = 'https://www.walmart.com/browse/'
    WALMART_DEPARTMENTS = [
        {'url': 'https://www.walmart.com/cp/electronics/3944'},
        {'url': 'https://www.walmart.com/cp/college-beyond-shop/8174172'},
        {'url': 'https://www.walmart.com/cp/back-to-school/1071204'},
        {'url': 'https://www.walmart.com/cp/pet-supplies/5440'},
        {'url': 'https://www.walmart.com/cp/spring-cleaning/4641200'},
        {'url': 'https://www.walmart.com/cp/auto-and-tires/91083'},
        {'url': 'https://www.walmart.com/cp/tires/1077064'},
        {'url': 'https://www.walmart.com/browse/personalized-gifts/4044_133224'},
        {'url': 'https://www.walmart.com/cp/walmart-paint-finder/7099662'},
        {'url': 'https://www.walmart.com/cp/heating/1161932'},
        {'url': 'https://www.walmart.com/cp/sewing/1094704'},
        {'url': 'https://www.walmart.com/cp/party-occasions/2637'},
        {'url': 'https://www.walmart.com/cp/air-quality/1231459'},
        {'url': 'https://www.walmart.com/cp/tools/1031899'},
        {'url': 'https://www.walmart.com/cp/heating/1161932'},
        {'url': 'https://www.walmart.com/cp/pro-tools/3972959'},
        {'url': 'https://www.walmart.com/cp/baby-products/5427'},
        {'url': 'https://www.walmart.com/cp/baby-registry/1229485'},
        {'url': 'https://www.walmart.com/cp/baby-toys-toddler-toys/491351'},
        {'url': 'https://www.walmart.com/cp/baby-strollers/118134'},
        {'url': 'https://www.walmart.com/cp/baby-feeding/133283'},
        {'url': 'https://www.walmart.com/cp/nursery-decor/414099'},
        {'url': 'https://www.walmart.com/cp/diapering-potty/486190'},
        {'url': 'https://www.walmart.com/cp/baby-gear/86323'},
        {'url': 'https://www.walmart.com/cp/baby-safety/132943'},
        {'url': 'https://www.walmart.com/cp/toddlers-room/978579'},
        {'url': 'https://www.walmart.com/cp/patio-garden/5428'},
        {'url': 'https://www.walmart.com/cp/beauty/1085666'},
        {'url': 'https://www.walmart.com/cp/7924299'},
        {'url': 'https://www.walmart.com/cp/sports-and-outdoors/4125'},
        {'url': 'https://www.walmart.com/cp/toys/4171'},
        {'url': 'https://www.walmart.com/cp/Home-Improvement/1072864'},
        {'url': 'https://www.walmart.com/cp/health/976760'},
    ]
