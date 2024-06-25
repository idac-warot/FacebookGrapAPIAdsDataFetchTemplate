import requests, facebook, os, json, time, glob2, pandas, numpy

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
app_id = ''
app_secret = ''

def clearDir(pathtodir):
    files = glob2.glob(pathtodir + "/*")
    for f in files:
        os.remove(f)

def write_json_to_file(json_input, filename):
    f = open(filename, "w")
    f.write(json.dumps(json_input, indent=4))
    f.close()


def get_longlive_token():
    # Opening JSON file
    f = open('token/short_token.json')
    data = json.load(f)
    user_short_lived_token_from_client = data['access_token']

    graph = facebook.GraphAPI(access_token=user_short_lived_token_from_client)
    # Extend the expiration time of a valid OAuth access token.
    extended_token = graph.extend_access_token(app_id=app_id, app_secret=app_secret)
    print(extended_token)  # verify that it expires in 60 days

    write_json_to_file(extended_token, "token/long_token.json")


def auth():
    # Opening JSON file
    f = open('token/long_token.json')
    data = json.load(f)
    long_lived_token = data['access_token']

    graph = facebook.GraphAPI(access_token=long_lived_token)

    profile = graph.get_object('me', fields='name')
    print(json.dumps(profile, indent=4))

    return graph


def fetchFacebookAdsAccountLevel(graph, account_id):
    #https: // developers.facebook.com / docs / marketing - api / insights / best - practices /

    input_fields = "name, campaigns{name, objective, adsets{name, ads{name,insights{spend,impressions,clicks}}}}"
   
    print("act_"+str(account_id))
    ads = graph.get_object("act_"+str(account_id), fields=input_fields)
    page = 1

    clearDir("output")
    while (True):
        try:
            print(page)
            write_json_to_file(ads, "output/page" + str(page) + ".json")
            page = page + 1
            time.sleep(0.5)

            print("campaigns" in ads)
            if "campaigns" in ads:
                ads = requests.get(ads['campaigns']['paging']['next']).json()
            else:
                print(ads['paging']['next'])
                ads = requests.get(ads['paging']['next']).json()

        except KeyError:
            print(KeyError)
            break
    

def jsontopandas():
    f = open("output/page1.json")
    raw_json = json.load(f)
    df1 = pandas.json_normalize(raw_json["campaigns"]["data"])
    df1.to_csv("output_csv/df.csv", index = False)

def main():
    get_longlive_token()
    graph = auth()
    fetchFacebookAdsAccountLevel(graph, "ad_account_id")
    jsontopandas()


if __name__ == "__main__":
    main()
