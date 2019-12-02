# Job Schema
Job advertisements on Indeed typically present a subset of the total information - for instance, salary is displayed on some but not all advertisements.  To build a comprehensive data model for jobs, we must determine a data model by looking at the domain of job schemas.

## Job Schema

| data_item       | Example                | data_type     | Notes     |
| -------------   | -------------          | ------------- |           |
| jobTitle        | Security Engineer      | string        |           |
| jobCompanyName  | Google                 | string        |           |
| jobLocation     | Melbourne, Sydney      | list[string]  |           |
| jobPeriod       | Full-time, Part-time   | list[string]  |           |
| jobSalary       | $25 - $35 an hour      | string        | Can be expressed as yearly wage | 
| jobDescription  | Google is...           | string        |           |
| jobPostDate     | UTC    | Datetime      | datetime      |           |

## Calculated Fields 


