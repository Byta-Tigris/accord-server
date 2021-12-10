from digger.base.request_manager import RequestManager



class InstagramRequestManager(RequestManager):
    
    def __init__(self) -> None:
        self.base_url = {
            "default": "https://graph.facebook.com/v3.2",
            "graph_v12": "https://graph.facebook.com/v12.0"
        }
        super().__init__(self.base_url)
    
    
    