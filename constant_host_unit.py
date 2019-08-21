#all the constants
INFRA_API = 'entity/infrastructure/hosts'
TIMESERIES_API="timeseries/com.dynatrace.builtin:host.availability?includeData=true&&relativeTime=10mins"
FETCH_APPLICATIONS = "entity/applications/"
FETCH_SYN_APPLICATIONS = "synthetic/monitors"
APP_BILLING_API = "metrics/series/builtin%3Abilling.apps.web.sessionsByApplication%3Afold(value)?pageSize=0&resolution=120&from=now-1w"
SYN_BILLING_API = "metrics/series/builtin%3Abilling.synthetic.actions%3Afold(value)?pageSize=0&resolution=120&from=now-1w"
HTTP_BILLING_API = "metrics/series/builtin%3Abilling.synthetic.requests%3Afold(value)?pageSize=0&resolution=120&from=now-1w"
#BILLING_API = "metrics/series/builtin%3Abilling.apps.web.sessionsByApplication%3Afold(value)?pageSize=0&resolution=120&from=now-1w"
