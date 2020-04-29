#!/usr/bin/env python

import os, argparse, requests, json, urllib.parse
from datetime import datetime
import subprocess

import config as cfg
import report

argParser = argparse.ArgumentParser()
argParser.add_argument("-d", "--domain", required = True, help = "Target domain")
argParser.add_argument("-e", "--exclude", required = False,
    help = "Exclude subdomains (not implemented)")


all_domains = []
dns_data_set = set()
filtered_dns_resp_container = []
cname_dns_resp_container = set()
possible_ns_takeover = []

wayback_params_result = set()
wayback_js_result = set()
wayback_php_result = set()
wayback_aspx_result = set()
wayback_jspurls_result = set()
hostalive_result = set()

def execute_shell(cmd):
    result = ""

    for k in range(cfg.general["cmd_attempt_counter"]):
        report.print_info_message("Attempt {} to run {}"\
            .format(k, cmd))
        try:
            result = subprocess.check_output([cmd], shell=True).decode("utf-8")
            return result
        except subprocess.CalledProcessError as e:
            report.print_error_message(e.output)
            continue
        break

    return result


def get_array_from_file(filename):
    result = []
    with open(filename) as file:
        result = file.readlines()
        result = [line.rstrip("\n") for line in result]
        return result

def save_list_to_file(filename, container):
    with open(filename, "w") as file:
        for row in container:
            file.write(row + "\n")
    return

# TODO: reimplement sublist3r as module which returns array
def sublist3r():
    report.print_info_message("sublist3r")
    os.system("{} -d {} -t {} -o {} > /dev/null"\
        .format(cfg.sublist3r["run_path"],
            cfg.input_data["domain"],
            cfg.sublist3r["thread_count"],
            cfg.sublist3r["out_filename"]))

    return get_array_from_file(cfg.sublist3r["out_filename"])

def certspotter():
    report.print_info_message("certspotter")
    result = set()
    response = requests.get(cfg.certspotter["format_url"]
        .format(cfg.input_data["domain"]))

    if response.status_code == requests.codes.ok:
        json_resp = json.loads(response.content)
        for cert in json_resp:
            for dns_name in cert["dns_names"]:
                if dns_name.find(cfg.input_data["domain"]) != -1:
                    result.add(dns_name)

    with open(cfg.certspotter["out_filename"], 'w+') as file:
        file.write('\n'.join(result))

    return list(result)

# TODO: remake ct to module which return an array
def nsrecords():
    # crtsh -> massdns
    report.print_info_message("massdns for crtsh result")
    os.system("{}/{} {} | {} -r {} -t A -q -o S -w {}"\
        .format(cfg.massdns["scripts_path"],
            cfg.massdns["crtsh_script_name"],
            cfg.input_data["domain"],
            cfg.massdns["run_path"],
            cfg.massdns["resolvers_path"],
            cfg.massdns["crtsh_out_file"]))
    
    # sublist3r -> massdns
    report.print_info_message("massdns for sublist3r result")
    os.system("cat {} | {} -r {} -t A -q -o S -w {}"\
        .format(cfg.sublist3r["out_filename"],
            cfg.massdns["run_path"],
            cfg.massdns["resolvers_path"],
            cfg.massdns["sublist3r_out_file"]))

    # certspotter -> massdns
    report.print_info_message("massdns for certspotter result")
    os.system("cat {} | {} -r {} -t A -q -o S -w {}"\
        .format(cfg.certspotter["out_filename"],
            cfg.massdns["run_path"],
            cfg.massdns["resolvers_path"],
            cfg.massdns["certspotter_out_file"]))

    # subbrute -> massdns
    report.print_info_message("massdns for subbrute result")
    os.system("{}/{} {} {} | {} -r {} -t A -q -o S | grep -v {} > {}"\
        .format(cfg.massdns["scripts_path"],
            cfg.massdns["subbrute_script_name"],
            cfg.massdns["word_list"],
            cfg.input_data["domain"],
            cfg.massdns["run_path"],
            cfg.massdns["resolvers_path"],
            cfg.massdns["some_ip"],
            cfg.massdns["subbrute_out_file"]))

    # dsn-resp: name, type, data
    report.print_info_message("Collct DNS responses")
    dns_resp_container = get_array_from_file(cfg.massdns["crtsh_out_file"]) \
        + get_array_from_file(cfg.massdns["sublist3r_out_file"]) \
        + get_array_from_file(cfg.massdns["certspotter_out_file"]) \
        + get_array_from_file(cfg.massdns["subbrute_out_file"])

    global dns_data_set, filtered_dns_resp_container, cname_dns_resp_container
    global possible_ns_takeover, all_domains

    dns_data_set = set([dns_resp.split()[2] for dns_resp in dns_resp_container])

    filtered_dns_resp_container = []
    cname_dns_resp_container = set()
    possible_ns_takeover = []
    all_domains = set(get_array_from_file(cfg.sublist3r["out_filename"])\
        + get_array_from_file(cfg.certspotter["out_filename"]))

    report.print_info_message("Process dns unique values, CNAMEs, NXDOMAINs")
    for dns_data in dns_data_set:
        for dns_resp in dns_resp_container:
            if dns_resp.find(dns_data) != -1:
                filtered_dns_resp_container.append(dns_resp)
                all_domains.add(dns_resp.split()[0][:-1])    # delete '.'

                if dns_resp.find("CNAME") != -1:
                    cname_dns_resp_container.add(dns_resp)

                    cname = dns_resp.split()[0]
                    try:
                        host_dns_lookup = execute_shell("host " + cname)
                        if host_dns_lookup.find("NXDOMAIN") != -1:
                            possible_ns_takeover.append(dns_resp)
                    except subprocess.CalledProcessError as e:
                        report.print_error_message(e.output)

                break

    save_list_to_file(cfg.general["all_domain_filename"], all_domains)

    #print("DEBUG: Print containers")
    #print("sublist3r = ", get_array_from_file(cfg.sublist3r["out_filename"]), "\n")
    #print("certspotter = ", certspotter(), "\n")
    #print("dns_resp_container = ", dns_resp_container, "\n")
    #print("dns_data_set = ", dns_data_set, "\n")
    #print("filtered_dns_resp_container = ", filtered_dns_resp_container, "\n")
    #print("cname_dns_resp_container = ", cname_dns_resp_container, "\n")
    #print("possible_ns_takeover = ", possible_ns_takeover, "\n")
    #print("all_domains = ", all_domains, "\n")
    return

# TODO: implement exclude domains
def exclude_domains():
    return


# TODO: httprobe pass params direct to stdin (not via file)
''' TODO-CHECKME: urllist.txt is filtered? if there are http and http
save only http url, if there is only http or https - asve this one.'''
def hostalive():
    report.print_info_message("hostalive")
    global hostalive_result

    responsive = execute_shell("cat {} | httprobe -c 50 -t 3000"\
        .format(cfg.general["all_domain_filename"])).split('\n')

    result = []
    http_result = set()
    https_result = set()

    for resp in responsive:
        if resp.find("http://") != -1:
            http_result.add(resp.replace("http://", ""))
        elif resp.find("https://") != -1:
            https_result.add(resp.replace("https://", ""))

    https_result = https_result - http_result # sort to unique https urls

    hostalive_result = http_result | https_result
    result = [ "http://" + url for url in http_result]\
        + [ "https://" + url for url in https_result]

    report.print_info_message("Total of {} live subdomains were found".format(len(result)))

    save_list_to_file(cfg.hostalive["out_filename"], result)
    return result

# stub
def cleandirsearch():
    return

# stub
def cleanup():
    return

def aqua():
    report.print_info_message("aqua")
    os.mkdir(cfg.aqua["out_folder_name"])
    #os.mkdir(cfg.aqua["out_folder_name"] + "/parsedjson")  

    os.system("cat {} | aquatone -chrome-path {} -out {} -threads {} -silent"\
        .format(cfg.hostalive["out_filename"],
            cfg.aqua["chromium_path"],
            cfg.aqua["out_folder_name"],
            cfg.aqua["countThreads"]))
    return

# TODO: remove working with tmp files; store info to array and pass it to app
# TODO: replace grep-s to python functions
def waybackrecon():
    report.print_info_message("waybackrecon")
    os.mkdir(cfg.waybackurls["out_folder_name"])

    os.system("cat {} | waybackurls > {}/{}"\
        .format(cfg.hostalive["out_filename"],
            cfg.waybackurls["out_folder_name"],
            cfg.waybackurls["out_filename"]))

    global wayback_params_result, wayback_js_result, wayback_php_result
    global wayback_aspx_result, wayback_jspurls_result

    wayback_params_result = execute_shell("cat {}/{} | sort -u | unfurl --unique keys"\
        .format(cfg.waybackurls["out_folder_name"],
            cfg.waybackurls["out_filename"]))

    wayback_params_result = wayback_params_result.split('\n')
    wayback_list = get_array_from_file(cfg.waybackurls["out_folder_name"]
        + "/" + cfg.waybackurls["out_filename"])

    for url in wayback_list:
        path = urllib.parse.urlparse(url).path
        ext = os.path.splitext(path)[1]
        if ext == ".js":
            wayback_js_result.add(url)  # TODO-CHECKME: or add(path)
        elif ext == ".php":
            wayback_php_result.add(url)
        elif ext == ".aspx":
            wayback_aspx_result.add(url)
        elif ext == ".jsp":
            wayback_jspurls_result.add(url)

    os.remove("{}/{}".format(
        cfg.waybackurls["out_folder_name"],
        cfg.waybackurls["out_filename"]))
    return

def dirsearcher():
    report.print_info_message("hostalive")
    os.system("cat {} | xargs -P {} -I % sh -c \"python3 {} -e php,asp,aspx,jsp,html,zip,jar -w {}\
        -t {} -u % | grep Target && tput sgr0\""\
        .format(cfg.hostalive["out_filename"],
            cfg.dirsearcher["subdomain_threads"],
            cfg.dirsearcher["run_path"],
            cfg.dirsearcher["dirsearch_wordlist"],
            cfg.dirsearcher["dirsearch_threads"]))
    return


def discovery():
    hostalive()
    cleandirsearch()
    aqua()
    cleanup()
    waybackrecon()
    dirsearcher()
    return


def generate_report():
    report.print_container("Total scanned subdomains", hostalive_result)

    report.print_text("aqua report path: ", os.getcwd() + "/" + cfg.aqua["out_folder_name"])

    # possible ns takeovers
    report.print_container("Possible NS Takeovers", possible_ns_takeover)

    # wayback
    report.print_container("Params wordlist", wayback_params_result)
    report.print_container("Javscript files", wayback_js_result)
    report.print_container("PHP Urls", wayback_php_result)
    report.print_container("ASP Urls", wayback_aspx_result)
    report.print_container("JSP Urls", wayback_jspurls_result)

    # dig and host
    dig_result = execute_shell("dig " + cfg.input_data["domain"])
    report.print_text("DIG INFO", dig_result)

    host_result = execute_shell("host " + cfg.input_data["domain"])
    report.print_text("HOST INFO", host_result)

    # nmap
    # TODO: report for subdomains
    nmap_args = "-sV -T3 -Pn -p {} {} | grep -E 'open|filtered|closed'"\
        .format(','.join(str(port) for port in cfg.nmap["ports"]), cfg.input_data["domain"])

    nmap_res = execute_shell("nmap " + nmap_args)
    report.print_text("NMAP INFO", nmap_res)

    return

def main():
    args = vars(argParser.parse_args())
    cfg.input_data["domain"] = args["domain"]
    cfg.input_data["excluded_domains"] = args["exclude"]

    cfg.general["domain_recon_path"] = "./{}-{}"\
    .format(cfg.input_data["domain"], datetime.now().strftime("%d-%m-%Y-%H:%M:%S"))

    # TODO: excaption handling
    os.mkdir(cfg.general["domain_recon_path"])
    os.chdir(cfg.general["domain_recon_path"])
    sublist3r()
    certspotter()
    nsrecords()
    discovery()

    generate_report()
    return

if __name__ == "__main__":
    main()