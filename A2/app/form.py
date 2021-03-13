from flask_wtf import FlaskForm
from wtforms import FloatField, IntegerField, SubmitField, validators


class AutoScalarForm(FlaskForm):
    cpu_threshold_grow = IntegerField('Cpu_Threshold_Grow', [validators.optional(), validators.NumberRange(min=0, max=100, message="Please specify range from 0 to 100")], filters=[lambda x: x or None])
    cpu_threshold_shrink = IntegerField('Cpu_Threshold_Shrink', [validators.optional(), validators.NumberRange(min=0, max=100, message="Please specify range from 0 to 100")], filters=[lambda x: x or None])
    expand_ratio = IntegerField('Expand_Ratio', [validators.optional(), validators.NumberRange(min=1, max=8, message="Please specify range from 1 to 8")], filters=[lambda x: x or None])
    shrink_ratio = FloatField('Shrink_Ratio', [validators.optional(), validators.NumberRange(min=0, max=1, message="Please specify range from 0 to 1")], filters=[lambda x: x or None])
    submit = SubmitField('Submit')
