# aws-parameter-store-backup
Simple dump/import backup for AWS Parameter Store Systems Manager.

## Requirements
* Python 3.7+
* [boto3](https://pypi.org/project/boto3/)
* Configured AWS SDK credentials and default region ([Quick start](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html#configuration) | [Full documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html))

## Usage
```
aws_ssm_parameter_backup.py  [-h] [-m {export,import}]
                             [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                             [-f REGEX]
                             [-s {ascending,descending}]
                             [-i INFILE | -o OUTFILE]
                             [-p PROFILE]
                             [-r REGION]

optional arguments:
  -h, --help            show this help message and exit
  -m {export,import}, --mode {export,import}
                        Export secrets (default) or import
  -l {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --loglevel {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        Logging/output verbosity
  -f REGEX, --filter REGEX
                        Filter secrets to import/export using a supplied regular expression
  -s {ascending,descending}, --sort {ascending,descending}
                        Sort secrets to export in ascending or descending order
  -i INFILE, --infile INFILE
                        Filename for import (default: stdin)
  -o OUTFILE, --outfile OUTFILE
                        Filename for export (default: stdout)

AWS configuration options:
  -p PROFILE, --profile PROFILE
                        Override AWS credentials/configuration profile
  -r REGION, --region REGION
                        Override AWS region
```

### Examples

**Example**
```bash
python3 aws_ssm_parameter_backup.py -m export -o parameter_store_dev.json -s ascending
```

**Output**
```json
{
  "Parameters": [
    {
      "Name": "test",
      "Type": "SecureString",
      "Value": "test 1234"
    }
  ]
}
```

