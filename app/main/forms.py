from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, PasswordField
from wtforms.validators import DataRequired


class ItemForm(FlaskForm):
    adress = StringField('Скопируйте сюда ссылку на товар: ')
    # name = StringField('Название товара: ')
    choice_category = SelectField('Выберите Категорию из списка: ', coerce=int)
    # choice_subcategory = SelectField('Выберите Подкатегорию: ', coerce=int)
    submit = SubmitField('Искать')
