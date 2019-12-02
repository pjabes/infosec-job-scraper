# Job Schema
Job advertisements on Indeed typically present a subset of the total information - for instance, salary is displayed on some but not all advertisements.  To build a comprehensive data model for jobs, we must determine a data model by looking at the domain of job schemas.

| data_item            | Example                         | data_type     | 
| -------------        | -------------                   | ------------- |
| jobTitle             | Security Engineer               | string        |
| jobCompanyName       | Google                          | string        |
| jobLocation          | Melbourne, Sydney               | list[string]  |
| jobPeriod            | Full-time, Part-time            | list[string]  |
| jobSalary            | $25 - $35 an hour               | string        |
| jobDescription       | MSS Security is Australia’s...  | string        |
| jobPostDate          | MSS Security - 4 days ago       | string        |