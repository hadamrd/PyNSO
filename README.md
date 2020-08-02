# NSOTAF test automation framework:

* API of test play book in this format:

```yaml
packages:
  - xxxx
  - ...
  - xxxx
devices:
  <DEVICE_NAME>:
    ned: <NED>
  ...
test-cases:
  <TEST01>:
    test-args
      device: <device_id>
      payload: <path_to_payload>
      show_output_cmd: <device_cli_cmd_to_get_test_output>
      [expect: <path_to_expect>]* (optional)
    [pre-clean-cmd: <cmd>]* (optional)
    [post-clean-cmd: <cmd>]* (optional)
  ...
```

* To run the test: `python taf.py name_of_playbook.yaml [-d] [-mn] [-pr] [-mp]` (or `./nsotaf.py` directly)
  * add the option `-d` to activate debut level logging
  * add option `-pr` to reload packages before test
  * add option `-mp` to make the list of packages before
  * add option `-mn` to create netsims for test devices
