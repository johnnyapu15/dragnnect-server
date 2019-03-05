class FCM:
    from pyfcm import FCMNotification
    FCM_API_KEY = "AAAANBr_rLA:APA91bEYgawceL8UA4Hh0X8SOiBwSrkTkO7Fw3cfj-hZEGG80ae8PE0NwVauKB60ZpQg1Q_bcsjMOdgox39h0o-HzpMzVtzIzGGEEX_3FvaYQMGmE3qou32s0Hun9kh9qnnpZGTxXo_d"
    PROXY_DICT = {"http": "http://101.101.162.213"}

    push_service = FCMNotification(api_key=FCM_API_KEY)
    db = ''
    
    def init(self, DB):
        self.db = DB
    def registryFCM(self, _USER_ID, _REG_ID):
        r = self.db.result(self.db.sal.select([self.db.FCM_TABLE], self.db.FCM_TABLE.c.user_id == _USER_ID))
        if len(r) == 0:
            ret = self.db.insert(
                self.db.FCM_TABLE,
                [
                    [
                        _USER_ID,
                        _REG_ID
                    ]
                ]
            )
        else:
            if r[0][0] != _REG_ID:
                ret = self.db.FCM_TABLE.update().\
                      where(self.db.FCM_TABLE.c.user_id == _USER_ID).\
                      values(device_key = _REG_ID)
                self.db.conn.execute(ret)
                ret = "Re-registry..."
            else:
                ret = "Registered id."
        return ret


    def pushToUserID(self, _USER_ID, _MSG_TITLE, _MSG_BODY, _CLK_ACT):
        s = self.db.sal.select([self.db.FCM_TABLE.c.device_key], self.db.FCM_TABLE.c.user_id == _USER_ID)
        res = self.db.result(s)
        push_id = res[0][0]
        push_service = self.FCMNotification(
            api_key=self.FCM_API_KEY,
            proxy_dict=self.PROXY_DICT)

        result = push_service.notify_single_device(
            registration_id=push_id, 
            message_title=_MSG_TITLE, 
            message_body=_MSG_BODY,
            click_action=_CLK_ACT
        )

        print(result)
        