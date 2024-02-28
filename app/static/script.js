setCookie = (cName, cValue, expDays) => {
    let date = new Date();
    date.setTime(date.getTime() + (expDays * 24 * 60 * 60 * 1000));
    const expires = "expires" + date.toUTCString();
    document.cookie = cName + "=" + cValue + expires + ";path=/, path=/login, path=/register";

}

document.querySelector("#cookies-btn").addEventListener("click"),() => {
    document.querySelector("#cookies").computedStyleMap.display = "none";
    setCookie("cookie", true, 30);
}