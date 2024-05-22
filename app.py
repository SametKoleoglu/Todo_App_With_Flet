import flet
from flet import *
from datetime import datetime
import sqlite3


class Database:
    def connect_database():
        try:
            db = sqlite3.connect("todo.db")
            c = db.cursor()
            c.execute(
                "CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY, task TEXT NOT NULL, date VARCHAR(255) NOT NULL)")
            return db
        except Exception as e:
            print(e)

    def read_database(db):
        c = db.cursor()
        c.execute("SELECT task, date FROM tasks")
        records = c.fetchall()
        return records

    def insert_database(db, values):
        c = db.cursor()
        c.execute("INSERT INTO tasks (task, date) VALUES (?, ?)", values)
        db.commit()

    def delete_database(db, val):
        c = db.cursor()
        c.execute("DELETE FROM tasks WHERE task=?", val)
        db.commit()

    def update_database(db, val):
        c = db.cursor()
        c.execute("UPDATE tasks SET task=? WHERE task=?", val)
        db.commit()


class FormContainer(UserControl):
    def __init__(self, func):
        self.func = func
        super().__init__()

    def build(self):
        return Container(
            width=300,
            height=60,
            bgcolor="bluegrey500",
            opacity=0,
            border_radius=40,
            margin=margin.only(left=-20, right=-20),
            animate=animation.Animation(400, "decelerate"),
            animate_opacity=200,
            padding=padding.only(top=45, bottom=45),
            content=Column(
                horizontal_alignment=CrossAxisAlignment.CENTER,
                controls=[
                    TextField(
                        width=250,
                        height=40,
                        color="white",
                        bgcolor="bluegrey500",
                        border_radius=40,
                        border=border.all(0.5, "black"),
                        filled=True,
                        border_color="transparent",
                        hint_text="Enter Task Here",
                        hint_style=TextStyle(color="black", size=12),
                    ),
                    IconButton(
                        content=Text("Add task"),
                        width=180,
                        height=40,
                        on_click=self.func,
                        style=ButtonStyle(
                            bgcolor={"": 'black'},
                            shape={"": RoundedRectangleBorder(radius=10), },
                        ),
                    ),
                ]
            )
        )


class create_task(UserControl):
    def __init__(self, task: str, date: str, func1, func2):
        self.task = task
        self.date = date
        self.func1 = func1
        self.func2 = func2
        super().__init__()

    def task_delete_edit(self, name, color, func):
        return IconButton(
            icon=name,
            width=30,
            icon_size=20,
            icon_color=color,
            opacity=0,
            animate_opacity=200,
            on_click=lambda e: func(self.get_container_instance()),
        )

    def get_container_instance(self):
        return self

    def show_icons(self, e):
        if e.data == "true":
            (
                e.control.content.controls[1].controls[0].opacity,
                e.control.content.controls[1].controls[1].opacity,
            ) = (1, 1)
            e.control.content.update()
        else:
            (
                e.control.content.controls[1].controls[0].opacity,
                e.control.content.controls[1].controls[1].opacity,
            ) = (0, 0)
            e.control.content.update()

    def build(self):
        return Container(
            width=300,
            height=60,
            border=border.all(0.85, "white54"),
            border_radius=8,
            on_hover=lambda e: self.show_icons(e),
            clip_behavior=ClipBehavior.HARD_EDGE,
            padding=10,
            content=Row(
                alignment=MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    Column(
                        spacing=1,
                        alignment=MainAxisAlignment.CENTER,
                        controls=[
                            Text(
                                value=self.task, size=10
                            ),
                            Text(
                                value=self.date, size=9, color="white54"
                            )
                        ]
                    ),
                    Row(
                        spacing=0,
                        alignment=MainAxisAlignment.CENTER,
                        controls=[
                            self.task_delete_edit(
                                icons.DELETE_ROUNDED, "red500", self.func1),
                            self.task_delete_edit(
                                icons.EDIT_ROUNDED, "white75", self.func2),
                        ]
                    )
                ]
            )
        )


def main(page: Page):
    page.horizontal_alignment = "center"
    page.vertical_alignment = "center"

    def add_task_to_screen(e):
        dateTime = datetime.now().strftime("%b %d, %Y %I:%M")

        db = Database.connect_database()

        Database.insert_database(
            db, (form.content.controls[0].value, dateTime))
        db.close()

        if form.content.controls[0].value:
            _main_column_.controls.append(
                create_task(
                    form.content.controls[0].value,
                    dateTime,
                    delete_function,
                    update_function,
                )
            )

            _main_column_.update()

            create_todo_task(e)

        else:
            db.close()
            pass

    def delete_function(e):

        db = Database.connect_database()
        Database.delete_database(
            db, (e.controls[0].content.controls[0].controls[0].value,))
        db.close()

        _main_column_.controls.remove(e)
        _main_column_.update()

    def update_function(e):
        form.height, form.opacity = 200, 1
        (
            form.content.controls[0].value,
            form.content.controls[1].content.value,
            form.content.controls[1].on_click,
        ) = (
            e.controls[0].content.controls[0].controls[0].value,
            "Update",
            lambda _: finalize_update(e),
        )
        form.update()

    def finalize_update(e):

        db = Database.connect_database()

        Database.update_database(
            db, (form.content.controls[0].value, e.controls[0].content.controls[0].controls[0].value,))

        e.controls[0].content.controls[0].controls[0].value = form.content.controls[0].value
        e.controls[0].content.update()
        create_todo_task(e)

    def create_todo_task(e):
        if form.height != 200:
            form.height, form.opacity = 200, 1
            form.update()
        else:
            form.height, form.opacity = 80, 0
            form.content.controls[0].value = None,
            form.content.controls[1].content.value = "Add content",
            form.content.controls[1].on_click = lambda e: add_task_to_screen(e)
            form.update()

    _main_column_ = Column(
        scroll="hidden",
        expand=True,
        alignment=MainAxisAlignment.START,
        controls=[
            Row(
                alignment=MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    Text("Todo App", color="white", size=20),
                    IconButton(icon=icons.ADD, icon_color="white",
                               on_click=lambda e: create_todo_task(e)),
                ],
            ),
            Divider(color="white", height=8),
        ]
    )

    page.add(
        Container(
            width=1500,
            height=800,
            margin=10,
            bgcolor="steelblue",
            alignment=alignment.center,
            content=Row(
                alignment=MainAxisAlignment.CENTER,
                vertical_alignment=CrossAxisAlignment.CENTER,
                controls=[
                    # Main Container
                    Container(
                        width=300,
                        height=600,
                        bgcolor="#0f0f0f",
                        border_radius=40,
                        border=border.all(0.5, "#ffffff"),
                        padding=padding.only(top=35, left=20, right=20),
                        clip_behavior=ClipBehavior.HARD_EDGE,

                        content=Column(
                            alignment=MainAxisAlignment.CENTER,
                            expand=True,
                            controls=[
                                # main column here
                                _main_column_,

                                # Form class here
                                FormContainer(lambda e: add_task_to_screen(e))
                            ]
                        )
                    )
                ]

            )
        )
    )

    page.update()

    form = page.controls[0].content.controls[0].content.controls[1].controls[0]

    # db = Database.connect_database()
    # rows = Database.read_database(db)
    # for row in rows:
    #     _main_column_.controls.append(create_task(row[1], row[2], delete_function, update_function))
    #     _main_column_.update()

    # _main_column_.update()


if __name__ == "__main__":
    flet.app(target=main)
