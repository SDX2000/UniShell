def visible(fmt="{}"):
    def realFormat(obj):
        obj.visible = True
        obj.fmt = fmt
        return property(obj)

    return realFormat
