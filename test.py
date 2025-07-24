class A:
    def __init__(self, auth: str = "default_auth"):
        self.auth = auth

    def B(self, b_name: str = "default_b"):
        return B(self.auth, b_name)


class B:
    def __init__(self, auth: str, b_name: str):
        self.auth = auth
        self.b_name = b_name

    def C(self, c_name: str = "default_c"):
        return C(self.auth, self.b_name, c_name)


class C:
    def __init__(self, auth: str, b_name: str, c_name: str):
        self.auth = auth
        self.b_name = b_name
        self.c_name = c_name

    def get(self, additional: str):
        print(f"auth={self.auth}, b_name={self.b_name}, c_name={self.c_name}, additional={additional}")

A("supersecret").B("Beta").C("Charlie").get("More")
