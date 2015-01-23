def visible(fmt="{}"):
    def realformat(obj):
        obj.visible = True
        obj.fmt = fmt
        return property(obj)

    return realformat
