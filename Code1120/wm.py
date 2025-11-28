class Clothes:
    def __init__(self,clothes_type,can_fade):
        self.type = clothes_type
        self.can_fade = can_fade
        self.status = "脏"
    
    def get_wet(self):
        print(f"衣服被打湿了")

    def become_clean(self):
        print("衣服变干净了")
        self.status = "干净"

    def __str__(self):
        return f"衣服(类型={self.type}, 掉色={self.can_fade}, 状态={self.status})"

class WashingMachine:
    def __init__(self,machine_type,capacity):
        self.type = machine_type
        self.capacity = capacity
        self.mode = "标准"
        self.is_lid_open = False
        self.is_power_on = False
        self.is_running = False
        
        self.contains_clothes = []

    def be_opened_lid(self):
        print("洗衣机：盖子被打开")
        self.is_lid_open = True

    def be_put_clothes(self,clothes_list):
        if self.is_lid_open:
            if len(self.contains_clothes) + len(clothes_list) <= self.capacity:
                self.contains_clothes.extend(clothes_list)
                print(f"洗衣机: 桶内被放入了 {len(clothes_list)} 件衣服")
            else:
                print(f"洗衣机: 容量不足，无法放入所有衣服！")
            
        else :
            print("洗衣机：盖子未打开，无法放入衣服")

    def be_closed_lid(self):
        print("洗衣机: 盖子被关上")
        self.is_lid_open = False

    def be_pressed_button(self):
        print("洗衣机：被按下按键")
        self.is_power_on = True

    def fill_water(self):
        print("洗衣机：正在进水")

    def wash_clothes(self):
        print("洗衣机：正在洗衣服")

        for clothes in self.contains_clothes:
            clothes.get_wet()
            clothes.become_clean()

    def drain_water(self):
        print("洗衣机: 正在下水")

    def spin_clothes(self):
        print("洗衣机: 正在甩干衣服")

    def be_opened_lid_after_wash(self):
        print("洗衣机: 洗衣结束后盖子被打开")
        self.is_lid_open = True
        self.is_running = False

    def start_washing(self):
        if not self.is_lid_open and self.is_power_on and self.contains_clothes:
            self.fill_water()
            self.wash_clothes()
            self.drain_water()
            self.spin_clothes()
            self.be_opened_lid_after_wash()
        else:
            print("洗衣机: 无法启动，检查盖子是否关闭、电源是否打开、桶内是否有衣服")

    def __str__(self):
        return f"洗衣机(类型={self.type}, 容量={self.capacity}, 模式={self.mode}, 盖子={'开' if self.is_lid_open else '关'}, 电源={'开' if self.is_power_on else '关'}, 衣服数量={len(self.contains_clothes)})"

class Person:
    def __init__(self,name):
        self.name = name
        self.held_clothes = []

    def pick_up_clothes(self,clothes_list):
        print(f"人({self.name}): 拿起 {len(clothes_list)} 件衣服")
        self.held_clothes.extend(clothes_list)

    def open_washing_machine_lid(self, machine):
        print(f"人({self.name}): 打开洗衣机的盖子")
        machine.be_opened_lid()

    def put_clothes_in_washing_machine(self,machine):
        print(f"人({self.name}): 把衣服放进洗衣机")
        machine.be_put_clothes(self.held_clothes)
        self.held_clothes = []

    def close_washing_machine_lid(self, machine):
        print(f"人({self.name}): 关上洗衣机的盖子")
        machine.be_closed_lid()

    def press_washing_machine_switch(self,machine):
        print(f"人({self.name}): 按下洗衣机的开关")
        machine.be_pressed_button()

    def press_quick_wash_mode(self,machine):
        print(f"人({self.name}): 按下快洗模式")
        machine.mode = "快洗"

    def press_start(self,machine):
        print(f"人({self.name}): 按下启动")
        machine.start_washing()

    def __str__(self):
        return f"人(姓名={self.name})"
        
if __name__ =="__main__":
    person = Person(name = "Avenir")
    print (person)

    clothes1 = Clothes("棉质",False)
    clothes2 = Clothes("牛仔",True)
    print(clothes1)
    print(clothes2)

    washing_machine = WashingMachine ("滚筒",10)
    print(washing_machine)

    print("\n——————开始洗衣服—————")
    person.pick_up_clothes([clothes1,clothes2])
    person.open_washing_machine_lid(washing_machine)
    person.put_clothes_in_washing_machine(washing_machine)
    person.close_washing_machine_lid(washing_machine)
    person.press_washing_machine_switch(washing_machine)
    person.press_quick_wash_mode(washing_machine)
    person.press_start(washing_machine)

    print("\n————洗衣后状态——————")
    print(clothes1)
    print(clothes2)
    print(washing_machine)

        
    
