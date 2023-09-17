from arcleaps_engine import ArchivalEngine

cookie = input("Enter cookie: ")
engine = ArchivalEngine(2019104424, cookie)
engine.get_all_tlm()