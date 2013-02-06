# -*- coding: utf-8 -*-
from django.db.models import F, Q
from django.core.management.base import NoArgsCommand

from modeltranslation.settings import DEFAULT_LANGUAGE
from modeltranslation.translator import translator
from modeltranslation.utils import build_localized_fieldname


class Command(NoArgsCommand):
    help = ('Updates the default translation fields of all or the specified '
            'translated application using the value of the original field.')

    def handle(self, **options):
        verbosity = int(options['verbosity'])
        if verbosity > 0:
            self.stdout.write("Using default language: %s\n" % DEFAULT_LANGUAGE)
        for model, trans_opts in translator._registry.items():
            if model._meta.abstract:
                continue
            if verbosity > 0:
                self.stdout.write("Updating data of model '%s'\n" % model)
            for fieldname in trans_opts.fields:
                def_lang_fieldname = build_localized_fieldname(fieldname, DEFAULT_LANGUAGE)

                # We'll only update fields which do not have an existing value
                q = Q(**{def_lang_fieldname: None})
                field = model._meta.get_field(fieldname)
                if field.empty_strings_allowed:
                    q |= Q(**{def_lang_fieldname: ""})

                model.objects.filter(q).rewrite(False).update(**{def_lang_fieldname: F(fieldname)})
