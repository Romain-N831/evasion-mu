from django import forms
from .models import Review

class ReviewForm(forms.ModelForm): # ModelForm creates a form based on
                                   # existing Review model
    class Meta:
        model = Review # tells Django that this form is based on the
                       # Review model defined in the models.py of Review

        fields = ["rating", "comment"] # ensures customers can enter only
                                       # a rating and comment through this form

        widgets = {  # controls how rating selector and comment box appears
            "rating": forms.Select(
                choices = [
                    (1, "1 - Poor"),
                    (2, "2 - Fair"),
                    (3, "3 - Good"),
                    (4, "4 - Very Good"),
                    (5, "5 - Excellent"),
                ]
            ),
            "comment": forms.Textarea( # creates a multi-line text box

                attrs={ # attributes - allows the adding of HTML attributes
                        # to a form field so we can customise the appearance
                        # and behaviour of the webpage

                    "placeholder": "Share your experience...", # displays a hint inside the box
                                                               # before the user types

                    "rows": 4, # text box will be approximatively four lines tall
                }
            ),
        }