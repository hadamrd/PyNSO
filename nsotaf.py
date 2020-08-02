#! /usr/bin/python3
import os
from src.pynso import PyNSO
import yaml
import argparse

taf = PyNSO(username='admin',
            password='admin',
            NCS_RUN_DIR="~/ncs-run",
            NETSIM_DIR='~/ncs-run/packages')


def parse_args():
    parser = argparse.ArgumentParser(description='Bytel nso test automation launcher')
    parser.add_argument('playbook', help='playbook name')
    parser.add_argument('-d', '--debug', action="store_true", help='Use this arg to set debug mode')
    parser.add_argument('-mp', '--make_packages', action="store_true", help='Use this arg to make packages')
    parser.add_argument('-pr', '--packages_reload', action="store_true", help='Use this arg to package reload')
    parser.add_argument('-mn', '--make_netsims', action="store_true", help='Use this arg to create test netsims')
    return parser.parse_args()


def os_mkdir(path):
    if not os.path.exists(path):
        os.mkdir(path)


def save_to_file(file_path, data):
    with open(file_path, "w+") as stream:
        if not data:
            stream.write("")
        else:
            stream.write(data)


def compare_expect(generated, target):
    if generated.replace(" ", "") != target.replace(" ", ""):
        _same, _added, _removed = taf.compare_configs(target, generated)
        raise Exception(f"Added and ExpectAdded doesnt match!\nremoved:\n{_removed}\nadded:{_added}")


def generic_test(test_name, device, payload, show_output_cmd=None, expect=None, output_cli=None):
    os_mkdir("tmp")
    taf.log.info(f"Saving {test_name} pre deploy config.")
    save_to_file("tmp/pre", taf.get_device_conf(device, show_output_cmd))
    taf.apply_template(payload)
    taf.log.info(f"Saving {test_name} post deploy config.")
    save_to_file("tmp/post", taf.get_device_conf(device, show_output_cmd))
    same, added, removed = taf.compare_configs("tmp/pre", "tmp/post")
    if same:
        taf.log.info("Warning pre and post configs are identical")
    if not output_cli:
        output_cli = f"tmp/{test_name}-output.cli"
    save_to_file(output_cli, added)
    taf.log.info(f"Saving {test_name} output cli.")
    if expect:
        compare_expect(added, open(expect, "r").read())
        taf.log.info(">>> Test ended successfully")

def create_netsim(device, ned):
    taf.make_netsim(device, ned)
    taf.start_netsim(device)
    if ned == 'cisco-iosxr-cli-7.21':
        taf.netsim_commit_conf(device, "tailfned api service-policy-list")
    taf.onboard_netsim(device)
    taf.sync_from(device)


def run_play_book(cli_arg):

    if cli_arg.debug:
        taf.set_debug()

    # Later on if we want to integrate make default authgroup
    # with open('settings.yaml', 'r') as f:
    #     settings = yaml.load(f.read(), Loader=yaml.FullLoader)
    # nso_settings = settings['nso-settings']
    # for name, kwargs in nso_settings['auth-groups'].items():
    #     taf.create_auth_group(name, **kwargs)

    with open(cli_arg.playbook, 'r') as f:
        test_bed = yaml.load(f.read(), Loader=yaml.FullLoader)

    try:
        if "setup-cmd" in test_bed:
            taf.commit_cmd(test_bed["setup-cmd"])

        if cli_arg.make_packages:
            for p in test_bed['packages']:
                taf.make_package(p)

        if cli_arg.packages_reload:
            taf.packages_reload()

        if cli_arg.make_netsims:
            taf.delete_netsims()
            for device, attrs in test_bed["devices"].items():
                create_netsim(device, attrs["ned"])

        if 'preparation-payloads' in test_bed:
            for payload in test_bed['preparation-payloads']:
                taf.apply_template(payload)

        for name, attrs in test_bed["test-cases"].items():
            if "pre-clean-cmd" in attrs:
                taf.commit_cmd(attrs["pre-clean-cmd"])

            generic_test(name, **attrs["test-args"])

            if "post-clean-cmd" in attrs:
                taf.commit_cmd(attrs["post-clean-cmd"])

    except Exception as e:
        taf.log.error(str(e), exc_info=True)

    if "tear-down-cmd" in test_bed:
        taf.commit_cmd(test_bed["tear-down-cmd"])

    # taf.delete_netsims()



if __name__ == "__main__":
    run_play_book(parse_args())




