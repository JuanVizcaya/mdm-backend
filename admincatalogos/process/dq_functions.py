# -*- coding: utf-8 -*-
from datetime import date

all = ['delete_field','concatenate','upper_strip','upper_strip_list','to_str','to_float','to_int','remove_spaces','rm_double_spaces','char_to_zero','replace_tilde','upper','strip','zfill2','zfill3','zfill4']

def delete_field(df,field):
    return df.drop(columns=field.name)

def concatenate(field_a,field_b):
    return field_a + field_b

def upper_strip(string):
    return string.strip().upper()

def upper_strip_list(lst):
    return [element.upper().strip() for element in lst]

def to_str(field):
    return field.astype(str)

def to_float(field):
    return field.astype(float)

def to_int(field):
    return field.astype(int)

def remove_spaces(field):
    return field.str.replace(' ','')

def rm_double_spaces(field):
    return field.str.replace('  ',' ')

def char_to_zero(field):
    filt = (field.str.isalnum())
    field[-filt] = 0
    return field

def replace_tilde(field):
    return field.str.replace('À','Á').replace('È','É').replace('Ì','Í').replace('Ò','Ó').replace('Ù','Ú')

def upper(field):
    return field.str.upper()

def strip(field):
    return field.str.strip()

def zfill2(field):
    return field.map('{:0>2}'.format)

def zfill3(field):
    return field.map('{:0>3}'.format)

def zfill4(field):
    return field.map('{:0>4}'.format)

def to_date(field):
    return field.astype(date)
