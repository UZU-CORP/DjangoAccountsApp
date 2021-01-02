# uzu-account-app

This is the official API documentation for the uzu-accounts-app Django Application.

uzu-accounts-app is a generic django application tailored to Single Page Applications that abstracts user authentication and verification from the rest of your project.

uzu-accounts-app will use the model set with `AUTH_USER_MODEL` in settings.py of your django project or the default user model of `django.contrib.auth`


## Installation

Download and install the package from PyPi:
````bash
pip install uzu-django-accounts
````

Add `AccountsApp.urls` to your project's URLConf
````Python
urlpatterns = [
	...
	path("accounts/", include("AccountsApp.urls"))
]
````

Add the AccountsApp to your `INSTALLED_APPS`:
````Python
INSTALLED_APPS = [
	...
	"AccountsApp.apps.AccountsappConfig"
]
````

Setup the `ACCOUNTS_APP` settings variable in settings.py
````Python
ACCOUNTS_APP = {
	"base_url": "",			# Base url pattern for the AccountsApp urls
	"redirect_link": "", 	# Link redirected to after link verification 
	"code_length": 3, 		# specifies the length of the verification code
	"sign_in_after_verification": False,		# Specify if to sign in after verification is successful
    "2fa_duration": 3, # Number of minutes for which two factor authentication tokens will be valid, this setting is not required if not using two factor authentication
}
````

Then apply migrations

````Bash
python manage.py migrate
````
## API 
The app communicates with the client-side using basic api calls. 

API responses have the following basic format:
````javascript
{
	status: Boolean,         //  status of the API call
	data: Object,  			 //  payload
	error: String            //  error string in case an error occurs (status == False)
}
````


### API List

NB: The illustrations below assume that the app's urls were mapped to the `accounts/` path.

#### 1. sign-in

````javascript
axios.post("/accounts/sign-in/", {
	...accountFields,
	keep_signed_in: true 		// keeps the user signed in (optional)
})
returns {signature: ""} // if two factor authentication is enabled
````

#### 2. verify-2fa

````javascript
axios.post("/accounts/verify-2fa/", {
	code: number,
	signature: string
})
````

#### 3. sign-up

````javascript
axios.post("/accounts/sign-up/", {
	...accountFields,
	keep_signed_in: true 		// keeps the user signed in (optional)
})
````


#### 4. sign-out
````javascript
axios.get("/accounts/sign-out/")
````


#### 5. authenticate
````javascript
axios.post("/accounts/authenticate/", {
	password: ""
})
````

#### 6. send-password-reset-code
````javascript
axios.post("/accounts/send-password-reset-code/", {
	USERNAME_FIELD: "",		// The key is the user name field of the user model in your application and the value is it's value
})
````

#### 7. reset-password
````javascript
axios.post("/accounts/reset-password/", {
	signature: "",		// field value used to verify that a client requested for the code, it is returned on posting to the /accounts/send-password-reset-link/ api
	code: "",			// verification code. This comes from the user's email 
	new_password: "",
})
````


#### 8. change-password
````javascript
axios.post("/accounts/change-password/", {
	new_password: "",
	old_password: ""
})
````

#### 9. send-email-verification-link
````javascript
axios.post("/accounts/send-email-verification-link/", {
	// requires that you are logged in
})
````

#### 10. send-email-verification-code
````javascript
axios.post("/accounts/send-email-verification-code/", {
	// requires that you are logged in
})
returns {signature: ""}
````

#### 11. verify-email-code
````javascript
axios.post("/accounts/verify-code/", {
	signature: "",		
	code: "",			
})
````

## Tip:
To install the app under the api namespace  and still have the non api  verification routes working normally, import  the  pages UrlConf like this:
````Python
urlpatterns = [
	...
	path("accounts/", include("AccountsApp.pages"))
]
````