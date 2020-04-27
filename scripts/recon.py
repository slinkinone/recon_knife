#!/usr/bin/env python

import os, argparse, requests, json
from datetime import datetime
from subprocess import check_output

import config as cfg

argParser = argparse.ArgumentParser()
argParser.add_argument("-d", "--domain", required = True, help = "Target domain")
argParser.add_argument("-e", "--exclude", required = False,
    help = "Exclude subdomains (not implemented)")


all_domains = []
dns_data_set = set()
filtered_dns_resp_container = []
cname_dns_resp_container = set()
possible_ns_takeover = []


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
	os.system("{} -d {} -t {} -o {} > /dev/null"\
		.format(cfg.sublist3r["run_path"],
			cfg.input_data["domain"],
			cfg.sublist3r["thread_count"],
			cfg.sublist3r["out_filename"]))

	return get_array_from_file(cfg.sublist3r["out_filename"])

def certspotter():
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
    print("DEBUG: massdns for crtsh result")
    os.system("{}/{} {} | {} -r {} -t A -q -o S -w {}"\
        .format(cfg.massdns["scripts_path"],
            cfg.massdns["crtsh_script_name"],
            cfg.input_data["domain"],
            cfg.massdns["run_path"],
            cfg.massdns["resolvers_path"],
            cfg.massdns["crtsh_out_file"]))
    
    # sublist3r -> massdns
    print("DEBUG: massdns for sublist3r result")
    os.system("cat {} | {} -r {} -t A -q -o S -w {}"\
        .format(cfg.sublist3r["out_filename"],
            cfg.massdns["run_path"],
            cfg.massdns["resolvers_path"],
            cfg.massdns["sublist3r_out_file"]))

    # certspotter -> massdns
    print("DEBUG: massdns for certspotter result")
    os.system("cat {} | {} -r {} -t A -q -o S -w {}"\
        .format(cfg.certspotter["out_filename"],
            cfg.massdns["run_path"],
            cfg.massdns["resolvers_path"],
            cfg.massdns["certspotter_out_file"]))

    # subbrute -> massdns
    print("DEBUG: massdns for subbrute result")
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
    print("DEBUG: Concat DNS responses")
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

    print("DEBUG: Process dns unique values, CNAMEs, NXDOMAINs")
    for dns_data in dns_data_set:
        for dns_resp in dns_resp_container:
            if dns_resp.find(dns_data) != -1:
                filtered_dns_resp_container.append(dns_resp)
                all_domains.add(dns_resp.split()[0][:-1])    # delete '.'

                if dns_resp.find("CNAME") != -1:
                    cname_dns_resp_container.add(dns_resp)

                    cname = dns_resp.split()[0]
                    host_dns_lookup = check_output(["host", cname])
                    if host_dns_lookup.find("NXDOMAIN") != -1:
                        possible_ns_takeover.append(dns_resp)
                break

    save_list_to_file(cfg.general["all_domain_filename"])

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
    print("DEBUG: hostalive")
    responsive = check_output(["cat {} | httprobe -c 50 -t 3000"\
        .format(cfg.general["all_domain_filename"])])

    result = []
    http_result = set()
    https_result = set()

    for resp in responsive:
        if resp.find("http://") != -1:
            http_result.add(resp.replace("http://", ""))
        elif resp.find("https://") != -1:
            https_result.add(resp.replace("https://", ""))

    https_result = https_result - http_result # sort to unique https urls
    result = [ "http://" + url for url in http_result]\
        + [ "https://" + url for url in https_result]

    print("DEBUG: Total of {} live subdomains were found".format(len(result)))

    save_list_to_file(cfg.hostalive["out_filename"])
    return result

# stub
def cleandirsearch():
    return

# stub
def cleanup():
    return

def aqua():
    print("DEBUG: aqua")

    os.mkdir(cfg.aqua["out_folder_name"])
    #os.mkdir(cfg.aqua["out_folder_name"] + "/parsedjson")  

    os.system("cat {} | aquatone -chrome-path {} -out {} -threads {} -silent"\
        .format(cfg.hostalive["out_filename"],
            cfg.aqua["chromium_path"],
            cfg.aqua["out_folder_name"],
            cfg.aqua["countThreads"]))
    return

# TODO: remove working with tmp files; store info to array and pass it to app
# TODO: remove grep-s to python functions
def waybackrecon():
    print("DEBUG: waybackrecon")

    os.mkdir(cfg.waybackurls["out_folder_name"])

    os.system("cat {} | waybackurls > {}/{}"\
        .format(cfg.hostalive["out_filename"],
            cfg.waybackurls["out_folder_name"],
            cfg.waybackurls["out_filename"]))

    os.system("cat {}/{} | sort -u | unfurl --unique keys > {}/{}"\
        .format(cfg.waybackurls["out_folder_name"],
            cfg.waybackurls["out_filename"],
            cfg.waybackurls["out_folder_name"],
            cfg.waybackurls["params_filename"]))

    os.system("cat {}/{} | sort -u | grep -P \"\\w+\\.js(\\?|$)\" | sort -u > {}/{}"\
        .format(cfg.waybackurls["out_folder_name"],
            cfg.waybackurls["out_filename"],
            cfg.waybackurls["out_folder_name"],
            cfg.waybackurls["jsurls_filename"]))

    os.system("cat {}/{} | sort -u | grep -P \"\\w+\\.php(\\?|$)\" | sort -u > {}/{}"\
        .format(cfg.waybackurls["out_folder_name"],
            cfg.waybackurls["out_filename"],
            cfg.waybackurls["out_folder_name"],
            cfg.waybackurls["phpurls_filename"]))

    os.system("cat {}/{} | sort -u | grep -P \"\\w+\\.aspx(\\?|$)\" | sort -u > {}/{}"\
        .format(cfg.waybackurls["out_folder_name"],
            cfg.waybackurls["out_filename"],
            cfg.waybackurls["out_folder_name"],
            cfg.waybackurls["aspxurls_filename"]))

    os.system("cat {}/{} | sort -u | grep -P \"\\w+\\.jsp(\\?|$)\" | sort -u > {}/{}"\
        .format(cfg.waybackurls["out_folder_name"],
            cfg.waybackurls["out_filename"],
            cfg.waybackurls["out_folder_name"],
            cfg.waybackurls["jspurls_filename"]))
    return

def dirsearcher():
    print("DEBUG: aqua")
    os.system("cat {} | xargs -P {} -I % sh -c \"python3 {} -e php,asp,aspx,jsp,html,zip,jar -w {}\
        -t {} -u % | grep Target && tput sgr0\""\
        .format(cfg.hostalive["out_filename"],
            cfg.dirsearcher["subdomain_threads"],
            cfg.dirsearcher["run_path"],
            cfg.dirsearcher["dirsearch_wordlist"],
            cfg.dirsearcher["dirsearch_threads"]))

    # TODO-CHECKME: Output of the above script should be passed to report master
    # && ./lazyrecon.sh -r $domain -r $foldername -r %
    return


def discovery():
    hostalive()
    cleandirsearch()
    aqua()
    cleanup()
    waybackrecon()
    dirsearcher()
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
    #print(cfg)
    sublist3r()
    certspotter()
    nsrecords()

    return

if __name__ == "__main__":
    main()