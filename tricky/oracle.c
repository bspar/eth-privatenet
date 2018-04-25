/*
 * Inspired by https://jansson.readthedocs.io/en/latest/_downloads/github_commits.c
 * (MIT license)
 */
#define _GNU_SOURCE

#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <stdio.h>
#include <sys/syscall.h>

#include <jansson.h>
#include <curl/curl.h>

// I hate using so many escapes - effectively replaces "" delim with ()
// Using __VA_ARGS__ works around the comma/arg "problem"
#define S(...) #__VA_ARGS__

#define BUFFER_SIZE  (256 * 1024)  /* 256 KB */
#define URL     "http://public-node:8545/"
#define FLAG1_LOC   "flag1"
#define DEBUG 1

#define NEWGUESS_TOPIC "0x8b4a1da1e9d54b88ebafc9ce4677a2ca4196693b1c8500b9d1fc58d96553c5fd"
#define UPGRADE_TOPIC "0x450db8da6efbe9c22f2347f7c2021231df1fc58d3ae9a2fa75d39fa446199305"
#define PUBLISH_HASH "0x979ea13b"
#define GETCHAL_HASH "0x759014f0"
#define SETFLAG_HASH "0x3438e82c"


void error(const char *msg) {
    printf("Error: %s\n", msg);
    fflush(stdout);
    // exit(-1);
}

void debugfmt(const char *fmt, const char *arg) {
    if(DEBUG) {
        printf(fmt, arg);
        putchar('\n');
        fflush(stdout);
    }
}

struct write_result
{
    char *data;
    int pos;
};

char *atohex(const char *ascii) {
    char *result = malloc(strlen(ascii)*2+4);
    result[0] = '0';
    result[1] = 'x';
    for(int i=0; i<strlen(ascii); i++) {
        sprintf(result+(i*2+2), "%x", ascii[i]);
    }
    return result;
}
char *btohex(char *data, int len) {
    char *result = malloc(len*2+5);
    result[0] = '0';
    result[1] = 'x';
    for(int i=0; i<len; i++) {
        sprintf(result+(i*2+2), "%02x", (unsigned)data[i]&0xffU);
    }
    result[len*2+3] = '\0';
    return result;
}

int bincmp(char *data1, char *data2, int len) {
    for(int i=0; i<len; i++) {
        if(data1[i] != data2[i]) return 0;
    }
    return 1;
}

static size_t write_response(void *ptr, size_t size, size_t nmemb, void *stream)
{
    struct write_result *result = (struct write_result *)stream;

    if(result->pos + size * nmemb >= BUFFER_SIZE - 1)
    {
        fprintf(stderr, "error: too small buffer\n");
        return 0;
    }

    memcpy(result->data + result->pos, ptr, size * nmemb);
    result->pos += size * nmemb;

    return size * nmemb;
}

char *post(char *url, char *postdata) {
    CURL *curl = NULL;
    CURLcode status;
    struct curl_slist *headers = NULL;
    char *data = NULL;
    long code;

    curl_global_init(CURL_GLOBAL_ALL);
    curl = curl_easy_init();
    if (!curl) error("Cannot init curl instance");
    data = malloc(BUFFER_SIZE);
    if(!data) error("Cannot malloc data");

    struct write_result write_result = {
        .data = data,
        .pos = 0
    };
    headers = curl_slist_append(headers, "content-type: application/json;");
    curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);

    curl_easy_setopt(curl, CURLOPT_URL, URL);

    curl_easy_setopt(curl, CURLOPT_POSTFIELDSIZE, (long) strlen(postdata));
    curl_easy_setopt(curl, CURLOPT_POSTFIELDS, postdata);

    curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, write_response);
    curl_easy_setopt(curl, CURLOPT_WRITEDATA, &write_result);

    status = curl_easy_perform(curl);
    if(status != 0) {
        fprintf(stderr, "error: unable to request data from %s:\n", url);
        fprintf(stderr, "%s\n", curl_easy_strerror(status));
        error("Can't perform curl, bailing");
    }

    curl_easy_getinfo(curl, CURLINFO_RESPONSE_CODE, &code);
    if(code != 200) {
        fprintf(stderr, "error: server responded with code %ld\n", code);
        data[write_result.pos] = '\0';
        debugfmt("data: %s", data);
        error("RPC error code, bailing");
    }

    curl_easy_cleanup(curl);
    curl_slist_free_all(headers);
    curl_global_cleanup();

    /* zero-terminate the result */
    data[write_result.pos] = '\0';
    debugfmt("sent: %s", postdata);
    debugfmt("recv: %s", data);

    return data;
}

char *getContractAddress() {
    FILE *fp = fopen("/root/shared/contract.txt", "r");
    if(!fp) {
        error("Cannot get contract address from /root/shared/contract.txt");
        return 0;
    }
    char *addr = malloc(128);
    fgets(addr, 128, fp);
    addr[strcspn(addr, "\r\n")] = 0;
    fclose(fp);
    return addr;
}
char *getMyAddress() {
    FILE *fp = fopen("/root/shared/account.txt", "r");
    if(!fp) {
        error("Cannot get my address from /root/shared/account.txt");
        return 0;
    }
    char *addr = malloc(128);
    fgets(addr, 128, fp);
    addr[strcspn(addr, "\r\n")] = 0;
    fclose(fp);
    return addr;
}

void getVersion() {
    char *data = S({"jsonrpc":"2.0","method":"web3_clientVersion","params":[],"id":420});
    char *text = post(URL, data);
    if(!text) error("Got no response from curl");
}

const char *getSha3(char *data) {
    json_t *sha3, *root;
    json_error_t err;
    char *text;
    data = atohex(data);
    char *postdata = malloc(sizeof(char) * 256);
    if(!postdata) error("Cannot malloc postdata");
    snprintf(postdata, sizeof(char)*256,
        S({"jsonrpc":"2.0","method":"web3_sha3","params":["%s"],"id":420}), data);
    text = post(URL, postdata);
    if(!text) error("Got no response from curl");
    free(postdata);

    root = json_loads(text, 0, &err);
    free(text);
    sha3 = json_object_get(root, "result");

    return json_string_value(sha3);
}

// returns account string
char *unlockAccount(char *password) {
    FILE *fp = fopen("/root/shared/account.txt", "r");
    if(!fp) {
        error("Cannot get address from /root/shared/account.txt");
        return 0;
    }
    char *buf = malloc(sizeof(char) * 128);
    char *postdata = malloc(sizeof(char) * 256);
    fgets(buf, 68, fp);
    buf[strcspn(buf, "\r\n")] = 0;
    snprintf(postdata, sizeof(char)*256,
        S({"jsonrpc":"2.0","method":"personal_unlockAccount","params":["%s","%s"],"id":420}),
        buf, password);
    post(URL, postdata);
    free(postdata);
    fclose(fp);
    return buf;
}

char *getFunc(char *funcname) {
    char *func = malloc(sizeof(char) * 12);
    char *sha3 = getSha3(funcname);
    snprintf(func, 11, "%s", sha3);
    return func;
}

char *publishChallenge(char *myaddr, char *contaddr, char *secretsha3) {
    char *postdata = malloc(sizeof(char) * 512);
    char *randomdata = malloc(32);
    syscall(SYS_getrandom, randomdata, 32, 0); // docker doesn't have modern glibc
    char *randomhex = btohex(randomdata, 32)+2; // don't want '0x'
    snprintf(postdata, sizeof(char)*512,
        S({"jsonrpc":"2.0","method":"eth_sendTransaction","params":[{"from":"%s", \
            "to":"%s", "gasPrice":"0x430E23400", "data":"%s%s%s"}],"id":420}),
        myaddr, contaddr, PUBLISH_HASH, secretsha3+2, randomhex);
    post(URL, postdata);
    free(postdata);
    free(randomhex-2);
    return randomdata;
}

char *installFilter(char *topic, char *contaddr) {
    char *postdata = malloc(sizeof(char) * 1024);
    char *data;
    json_t *filterID, *root;
    json_error_t err;
    snprintf(postdata, sizeof(char)*1024,
        S({"jsonrpc":"2.0","method":"eth_newFilter","params":[{"address": \
            "%s", "topics":["%s"], "fromBlock":"latest",\
            "toBlock":"latest"}],"id":420}),
        contaddr, topic);
    data = post(URL, postdata);
    free(postdata);

    root = json_loads(data, 0, &err);
    free(data);
    filterID = json_object_get(root, "result");
    return json_string_value(filterID);
}

json_t *getEvents(char *filterID) {
    char *postdata = malloc(sizeof(char) * 1024);
    char *data;
    json_t *root;
    json_error_t err;
    snprintf(postdata, sizeof(char)*1024,
        S({"jsonrpc":"2.0","method":"eth_getFilterChanges",\
            "params":["%s"],"id":420}),
        filterID);
    data = post(URL, postdata);
    free(postdata);
    root = json_loads(data, 0, &err);
    free(data);
    return json_object_get(root, "result");
}

char *getChallenge(char *contaddr, char *myaddr) {
    char *postdata = malloc(sizeof(char) * 1024);
    char *data;
    char *chal = malloc(sizeof(char) * 36);
    json_t *root;
    json_error_t err;
    snprintf(postdata, sizeof(char)*1024,
        S({"jsonrpc":"2.0", "method":"eth_call", "params":[{"from": \
            "%s", "to": "%s", "data":"%s"}, "latest"], "id":420}),
        myaddr, contaddr, GETCHAL_HASH);
    data = post(URL, postdata);
    free(postdata);
    root = json_loads(data, 0, &err);
    free(data);
    data = json_string_value(json_object_get(root, "result"));
    for(int j=0; j<(strlen(data)/2-2); j++) {
        sscanf(data+(j*2+2), "%02hhx", chal+j);
    }
    json_decref(root);
    return chal;
}

int doGuessEvents(char *guessID, char *contaddr, char *myaddr, char *randomdata) {
    json_t *logs = getEvents(guessID);
    json_t *record;
    int i=0, j=0;
    char *data;
    char guess[36];
    for(i=0; i<json_array_size(logs); i++) {
        record = json_array_get(logs, i);
        data = json_string_value(json_object_get(record, "data"));
        debugfmt("got a log: %s", data);
        for(j=0; j<(strlen(data)/2-2); j++) {
            sscanf(data+(j*2+2), "%02hhx", guess+j);
        }
        debugfmt("Sanity check log: %s", guess);
        if(bincmp(getChallenge(contaddr, myaddr), guess, 32)) {
            error("Someone won by brute force!");
            return 1;
        } else {
            error("Someone won a challenge from a different publisher");
            return 2;
        }
    }
    json_decref(logs);
    return 0;
}

void setFlag(char *location) {
    char *postdata = malloc(sizeof(char) * 1024);
    char dataIndex[65] = "0000000000000000000000000000000000000000000000000000000000000020";
    char dataLen[65];
    char rightPadding[65];
    char *contaddr = getContractAddress();
    char *myaddr = getMyAddress();
    FILE *fp = fopen(location, "r");
    if(!fp) {
        error("Cannot open flag1 or flag2");
        exit(-1);
    }
    char *buf = malloc(sizeof(char) * 128);
    fgets(buf, 128, fp);
    buf[strcspn(buf, "\r\n")] = 0;

    snprintf(dataLen, 65,
        "00000000000000000000000000000000000000000000000000000000000000%02x",
        (unsigned int) strlen(buf));
    for(int i=0; i<(32-strlen(buf)%32); i++) {
        rightPadding[i*2] = '0';
        rightPadding[i*2+1] = '0';
    }
    rightPadding[2*(32-strlen(buf)%32)] = '\0';

    snprintf(postdata, sizeof(char)*1024,
        S({"jsonrpc":"2.0","method":"eth_sendTransaction","params":[{"from":"%s", \
            "to":"%s", "gasPrice":"0x430E23400", "data":"%s%s%s%s%s"}],"id":420}),
        myaddr, contaddr, SETFLAG_HASH, dataIndex, dataLen, atohex(buf)+2, rightPadding);
    post(URL, postdata);
    fclose(fp);
    free(buf);
    free(postdata);
}

char *doUpgradeEvents(char *guessID) {
    json_t *logs = getEvents(guessID);
    json_t *record;
    char *data;
    char *newcontaddr = 0;
    for(int i=0; i<json_array_size(logs); i++) {
        newcontaddr = malloc(68);
        record = json_array_get(logs, i);
        data = json_string_value(json_object_get(record, "data"));
        snprintf(newcontaddr, 68, "0x%s", data+26);
        debugfmt("got an upgrade request: %s", newcontaddr);
    }
    json_decref(logs);
    return newcontaddr;
}

void uninstallFilter(char *filterID) {
    char *postdata = malloc(sizeof(char) * 512);
    char *data;
    snprintf(postdata, sizeof(char)*512,
        S({"jsonrpc":"2.0","method":"eth_uninstallFilter","params":["%s"],"id":420}),
        filterID);
    free(post(URL, postdata));
    free(postdata);
    return;
}

int main(int argc, char *argv[]) {
    const char *sha3;
    char *guessID, *upgradeID, *randomdata;
    char *contaddr = getContractAddress();
    char *newcontaddr = 0;

    getVersion();
    if(argc != 2) {
        error("usage: oracle SECRET");
        exit(-1);
    }

    char *myaddr = unlockAccount(argv[1]);
    randomdata = publishChallenge(myaddr, contaddr, getSha3(argv[1]));

    debugfmt("filter topic 1: %s", NEWGUESS_TOPIC);
    debugfmt("filter topic 2: %s", UPGRADE_TOPIC);
    guessID = installFilter(NEWGUESS_TOPIC, contaddr);
    upgradeID = installFilter(UPGRADE_TOPIC, contaddr);
    for(int i=0; i < 18; i++) {
        sleep(10);
        if(doGuessEvents(guessID, contaddr, myaddr, randomdata)) {
            setFlag(FLAG1_LOC);
        }
        newcontaddr = doUpgradeEvents(upgradeID);
        if(newcontaddr) {
            free(contaddr);
            contaddr = newcontaddr;
            i = 0;
            debugfmt("Upgrading to new contract: %s", contaddr);
            guessID = installFilter(NEWGUESS_TOPIC, contaddr);
            upgradeID = installFilter(UPGRADE_TOPIC, contaddr);
            myaddr = unlockAccount(argv[1]);
            randomdata = publishChallenge(myaddr, contaddr, getSha3(argv[1]));
            newcontaddr = 0;
        }
    }

    // !!!! remove filter !!!!
    return 0;
}
