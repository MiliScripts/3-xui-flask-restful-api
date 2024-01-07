var cfIPv4 = []
var cfIPv4ToScan = []
const noOfEachRange24 = 30
const client = new XMLHttpRequest();
client.open('GET', 'https://raw.githubusercontent.com/vfarid/cf-ip-scanner/main/ipv4.txt');
client.onreadystatechange = function() {
  cfIPv4 = client.responseText.split("\n").map((cidr) => cidr.trim()).filter((cidr) => isCIDR(cidr));
  document.getElementById('btn-start').disabled = false;
  const tbody = document.getElementById('ip-ranges-body');
  cfIPv4.forEach((cidr) => {
    const row = tbody.insertRow();
    const cell = row.insertCell();
    cell.appendChild(document.createTextNode(cidr));
  })
}
client.send();
let mciIP = "hamrah.meowcdn.site";
let rtlIP = "rightel.meowcdn.site";
let mtnIP = "irancell.meowcdn.site";
let wifiIP = "wifi.meowcdn.site"


let maxIP;
let testNo;
let validIPs;
let maxLatency;
let numberOfWorkingIPs;
let ipRegex;
let immediateStop = false;
let progressBar = document.getElementById('progress-bar');
let progress = 0;
let language = localStorage.getItem('lang') || 'fa'

document.getElementById('max-ip').value = localStorage.getItem('max-ip') || 20;
document.getElementById('max-latency').value = localStorage.getItem('max-latency') || 400;
document.getElementById('ip-regex').value = localStorage.getItem('ip-regex');
document.getElementById('ip-include').value = localStorage.getItem('ip-include');
document.getElementById('ip-exclude').value = localStorage.getItem('ip-exclude');
setLang(language)

function setLang(lang) {
  if (lang == 'fa') {
    document.getElementById('body').style.direction = 'rtl';
  } else {
    document.getElementById('body').style.direction = 'ltr';
  }
  let elements = document.getElementsByClassName('btn-lang');
  [].forEach.call(elements, (el) => {
    el.classList.remove('btn-primary')
    el.classList.add('btn-outline-primary')
  })
  document.getElementById('btn-' + lang).classList.remove('btn-outline-primary')
  document.getElementById('btn-' + lang).classList.add('btn-primary')
  elements = document.getElementsByClassName('lang-field');
  [].forEach.call(elements, (el) => {
    el.style.display = 'none';
  })
  elements = document.getElementsByClassName('lang-' + lang);
  [].forEach.call(elements, (el) => {
    el.style.display = 'inline';
  })
  localStorage.setItem('lang', lang);
  language = lang;
}

document.getElementById('btn-en').onclick = () => {
  setLang('en')
}
document.getElementById('btn-fa').onclick = () => {
  setLang('fa')
}

function cancelScan() {
  immediateStop = true;
  document.getElementById('btn-start').disabled = false;
  document.getElementById('max-ip').disabled = false;
  document.getElementById('max-latency').disabled = false;
  document.getElementById('ip-regex').disabled = false;
  document.getElementById('ip-include').disabled = false;
  document.getElementById('ip-exclude').disabled = false;
  document.getElementById('btn-cancel').disabled = true;
}

let ips = [];

function startScan() {
  maxIP = ~~document.getElementById('max-ip').value;
  maxLatency = ~~document.getElementById('max-latency').value;
  ipRegex = document.getElementById('ip-regex').value;
  ipInclude = document.getElementById('ip-include').value;
  ipExclude = document.getElementById('ip-exclude').value;

  localStorage.setItem('max-ip', maxIP);
  localStorage.setItem('max-latency', maxLatency);
  localStorage.setItem('ip-regex', ipRegex);
  localStorage.setItem('ip-include', ipInclude);
  localStorage.setItem('ip-exclude', ipExclude);

  testNo = 0;
  numberOfWorkingIPs = 0;
  validIPs = [];
  document.getElementById('result').innerHTML = '';
  document.getElementById('btn-start').disabled = true;
  document.getElementById('max-ip').disabled = true;
  document.getElementById('max-latency').disabled = true;
  document.getElementById('ip-regex').disabled = true;
  document.getElementById('ip-include').disabled = true;
  document.getElementById('ip-exclude').disabled = true;
  document.getElementById('test-no').innerText = '';
  document.getElementById('btn-cancel').disabled = false;

  setTimeout(() => {
    let ips = processIPs()
    ips = randomizeElements(ips)
    testIPs(ips);
  }, 50)
}

function processIPs() {
  let ips = [];
  let regex = null;
  let excludeRegex = null;
  if (ipRegex) {
    regex = new RegExp(ipRegex);
  }
  if (ipInclude) {
    cfIPv4ToScan = makeCIDR(ipInclude);
  } else {
    cfIPv4ToScan = [...cfIPv4];
  }
  if (ipExclude) {
    excludeRegex = new RegExp(
      ipExclude.split(',').map(c => {return '^' + c.replaceAll('.', '\\.').replaceAll('/', '\\/')}).join('|')
    );
  }

  for (const cidr of cfIPv4ToScan) {
    if (regex && !regex.test(cidr)) {
      continue;
    }
    if (excludeRegex && excludeRegex.test(cidr)) {
      continue;
    }
    ips = ips.concat(cidrToRandomIPArray(cidr));
  }
  return ips
}



async function testIPs(ipList) {
  for (const ip of ipList) {
    if (immediateStop) {
      break;
    }
    testNo++;
    var testResult = 0;
    const url = `https://${ip}:2096/__down`;
    const startTime = performance.now();
    const controller = new AbortController();
    const multiply = maxLatency <= 500 ? 1.5 : (maxLatency <= 1000 ? 1.2 : 1);
    var timeout = 1.5 * multiply * maxLatency;
    var chNo = 0;
    for (const ch of ['', '|', '/', '-', '\\']) {
      const timeoutId = setTimeout(() => {
        controller.abort();
      }, timeout);
      if (ch) {
        timeout = 1 * multiply * maxLatency;
        document.getElementById('test-no').innerText = `#${testNo}:`;
        document.getElementById('ip-no').innerText = ip;
        document.getElementById('ip-no').style = `color: green`;
        document.getElementById('ip-try').innerText = ch;
        document.getElementById('ip-latency').innerText = Math.floor((performance.now() - startTime) / chNo) + 'ms';
      } else {
        timeout = 1.2 * multiply * maxLatency;
        document.getElementById('test-no').innerText = `#${testNo}:`;
        document.getElementById('ip-no').innerText = ip;
        document.getElementById('ip-no').style = `color: red`;
        document.getElementById('ip-try').innerText = '';
        document.getElementById('ip-latency').innerText = '';
      }
      try {
        const response = await fetch(url, {
          signal: controller.signal,
        });

        testResult++;
      } catch (error) {
        if (error.name === "AbortError") {
          //
        } else {
          testResult++;
        }
      }
      clearTimeout(timeoutId);
      chNo++;
    }

    const latency = Math.floor((performance.now() - startTime) / 5);

    if (testResult === 5 && latency <= maxLatency) {
      numberOfWorkingIPs++;
      validIPs.push({ip: ip, latency: latency});
      const sortedArr = validIPs.sort((a, b) => a.latency - b.latency);
      const tableRows = sortedArr.map(obj => `
        <tr>
          <td></td>
          <td>${obj.ip}</td>
          <td>${obj.latency}ms</td>
          <td>
          <button class="btn btn-outline-secondary btn-sm" onclick="copyToClipboard('${obj.ip}')"><img height="16px" src="assets/icon-copy.png" /></button>
          </td>
        </tr>`).join('\n');
      document.getElementById('result').innerHTML = tableRows;
    }

    if (numberOfWorkingIPs >= maxIP) {
      break;
    }
  }

  document.getElementById('ip-no').innerText = '';
  document.getElementById('ip-try').innerText = '';
  document.getElementById('ip-latency').innerText = '';
  document.getElementById('btn-start').disabled = false;
  document.getElementById('max-ip').disabled = false;
  document.getElementById('max-latency').disabled = false;
  document.getElementById('ip-regex').disabled = false;
  document.getElementById('ip-include').disabled = false;
  document.getElementById('ip-exclude').disabled = false;
  document.getElementById('btn-cancel').disabled = true;

  if (immediateStop) {
    immediateStop = false;
    document.getElementById('test-no').innerHTML = `
      <span class="lang-field lang-fa text-danger fw-bold">لغو شد!</span>
      <span class="lang-field lang-en text-danger fw-bold">Canceled!</span>  
    `;
  } else {
    if (window.self !== window.top) {
      window.top.postMessage(validIPs.map(el => el.ip).join('\n'), '*');
    }

    document.getElementById('test-no').innerHTML = `
    <div id="loading">درحال تمیز کردن آیپی ها لطفا صبر کنید ... 🕠</div>
<div id="done">آیپی های تمیز با موفقیت جایگذاری شد</div>
<div class="container border rounded-2 mt-2 border-dark">
  <p>اسکن آیپی ها به پایان رسید اپراتور مورد نظر را برای آپدیت کردن آیپی تمیز انتخاب کنید</p>
  <div class="row my-2">
    <div class="col-12 my-1">
      <button id="update" class="btn btn-success btn-lg rounded-2 fw-bold" type="button" onclick="ChangeIP(rtlIP)">
        جایگذاری آیپی رایتل
      </button>
    </div>
  </div>
  <div class="row my-2">
    <div class="col-12 my-1">
      <button type="button" class="btn btn-success btn-lg rounded-2 fw-bold" onclick="ChangeIP(mtnIP)">
        جایگذاری آیپی ایرانسل
      </button>
    </div>
  </div>
  <div class="row my-2">
    <div class="col-12 my-1">
      <button type="button" class="btn btn-success btn-lg rounded-2 fw-bold" onclick="ChangeIP(mciIP)">
        جایگذاری آیپی همراه اول
      </button>
    </div>
  </div>
  <div class="row my-2">
    <div class="col-12 my-1">
      <button type="button" class="btn btn-success btn-lg rounded-2 fw-bold" onclick="ChangeIP(wifiIP)">
        جایگذاری آیپی وایفای
      </button>
    </div>
  </div>
</div>
      

    `;
  }
 
}

function copyToClipboard(ip) {
  window.navigator.clipboard.writeText(ip).then(() => {
    alert('آی‌پی‌ در کلیپ‌بورد کپی شد.');
  }).catch(() => {
    alert('مشکلی پیش آمده است!');
  });
}

function copyAllToClipboard(ip) {
  const txt = validIPs.map(el => el.ip).join('\n');
  copyToClipboard(txt)
}

function isCIDR(cidr) {
  return cidr.match(/^([0-9]{1,3}\.){3}[0-9]{1,3}\/(16|17|18|19|20|21|22|23|24)$/g);
}

function makeCIDR(includeStr) {
  let includeList = includeStr.split(',').map((cidr) => cidr.trim());
  cidrList = includeList.flatMap((cidr) => {
    if (isCIDR(cidr)) {
      return [cidr];
    } else if (cidr) {
      const regex = new RegExp(
        '^' + cidr.replaceAll('.', '\\.').replaceAll('/', '\\/')
      );
      return cfIPv4.filter((cidr) => cidr.match(regex));
    } else {
      return [];
    }
  })
  return cidrList;
}

function generateRandomNumbers(count) {
  const numbers = [];
  while (numbers.length < count) {
    const randomNumber = Math.floor(Math.random() * 254) + 1;
    if (!numbers.includes(randomNumber)) {
      numbers.push(randomNumber);
    }
  }
  return numbers;
}

function splitCIDRTo24Ranges(cidr) {
  const [baseIP, baseMask] = cidr.split('/');
  const baseStart = baseIP.split('.').reduce((acc, octet) => (acc << 8) | parseInt(octet, 10), 0) >>> 0;
  const baseEnd = (baseStart | (0xffffffff >>> parseInt(baseMask, 10))) >>> 0;

  const ranges = [];
  let currentStart = baseStart;

  while (currentStart <= baseEnd) {
    ranges.push(currentStart);
    currentStart += 0x100;
  }

  return ranges
}


function cidrToRandomIPArray(cidr, count) {
  const ranges = splitCIDRTo24Ranges(cidr);
  const ips = [];
  for (const start of ranges) {
    const prefix = `${(start >>> 24) & 0xff}.${(start >>> 16) & 0xff}.${(start >>> 8) & 0xff}`;
    for (const no of generateRandomNumbers(noOfEachRange24)) {
      ips.push(prefix + '.' + no);
    }
  }
  return ips;
}

function randomizeElements(arr) {
  return [...arr].sort(() => {return 0.5 - Math.random()});
}


function showLoading() {
  document.getElementById('loading').style.display = 'block';
}

function hideLoading() {
  document.getElementById('loading').style.display = 'none';
}

function showDone() {
  document.getElementById('done').style.display = 'block';
  document.body.classList.add('done');
}

function ChangeIP(subdomain) {
  console.log('meow')
  // Show loading animation
  showLoading();
  // Create a sample JSON object
  var jsonData = {
    ips: validIPs.map(el => el.ip).join(','),
    subdomain: subdomain
  };
  // Define the URL where you want to post the JSON
  var postUrl = "http://localhost:5000/cf/update";
  // Use the Fetch API to make a POST request
  fetch(postUrl, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(jsonData)
  })
  .then(response => response.json())
  .then(data => {
    // Hide loading animation
    hideLoading();
    // Handle the response data here if needed
    console.log(data);
    // Show "Done" message and change background color on success
    showDone();
  })
  .catch(error => {
    // Hide loading animation in case of an error
    hideLoading();
    // Handle errors here
    console.error('Error:', error);
  });
}