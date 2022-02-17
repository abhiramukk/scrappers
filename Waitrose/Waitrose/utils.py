

def get_payload(category, start):
    if start == -1:
        return  {
                "customerSearchRequest": {
                    "queryParams": {
                        "size": 128,
                        "category": category,
                        "filterTags": [],
                        "sortBy": "MOST_POPULAR",
                        "orderId": "0"
                        }
                }
            }
    
    return  {
                "customerSearchRequest": {
                    "queryParams": {
                        "size": 128,
                        "category": category,
                        "filterTags": [],
                        "sortBy": "MOST_POPULAR",
                        "orderId": "0",
                        "start": start
                        }
                }
            }
         


def validate(data, keys):
    for key in keys:
        if key in data:
            data = data[key]
        else:
            return ""
    return data