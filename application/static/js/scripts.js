const hash = document.location.hash;

if (hash) {
	$('.nav-tabs a[href="' + hash + '"]').tab('show');

	const div = document.getElementById(hash.replace('#', ''));
	div.classList.add("active");
	window.scrollTo(0, 0);
}
else {
	document.getElementById("content").classList.add("active");
}

$('.nav-tabs a').on('shown.bs.tab', function (e) {
	window.location.hash = e.target.hash;
});

/* Used to validate the user input on the registration form. This is client-side only! */
function validateRegister() {

	const handle = document.getElementById("hadle").value;

	if (handle.length < 4) {
		alert("Profiilinimen pitää olla vähintään 4 merkkiä.");
		return false;
	} else if (handle.length > 12) {
		alert("Profiilinimi ei saa olla yli 12 merkkiä.");
		return false;
	}

	const password = document.getElementById("password").value;
	const password2 = document.getElementById("password2").value;

	if (password.length < 8) {
		alert("Salasanan pitää olla vähintään 8 merkkiä.");
		return false;
	} else if (password.length > 32) {
		alert("Salasana saa olla korkeintaan 32 merkkiä.");
		return false;
	}

	if (password !== password2) {
		alert("Molempien salasanojen pitää olla samat.");
		return false;
	}

	sessionStorage.setItem("account_created", true.toString());

	return true;
}

/* Used by the tag cloud. */
function searchByTagId(id) {
	document.location = "/search_with_tag/tag/" + id;
}

/* Removes the selected tag from the currently logged-in user using POST. */
function removeTag(id) {
	const c = confirm('Haluatko varmasti poistaa valitsemasi merkin?\n\nVoit aina myöhemmin lisätä sen uudestaan.');
	if (true === c) {
		del("/profile/tags/remove", "tag_id", id);
		/* Creates an HTML form to do POST with. */
		return true;
	}
	return false;
}

/* Nothing to see here, move along! No Base64 encoding used at all. */
function fillEmail() {
	const emailElement = document.getElementById("contact");
	const action = "YldGcGJIUnY=";
	const user = "Z290b25vZGU=";
	const domain = "b3V0bG9vay5jb20=";
	emailElement.href = atob(atob(action)) + ":" + atob(user) + atob("QA==") + atob(domain);
	emailElement.click();
}

/* Generates an HTML form that is then added to the DOM, pre-filled and submitted.*/
function del(path, name, id, id2) {
	const form = document.createElement("form");
	form.setAttribute("method", "POST");
	form.setAttribute("action", path);

	const idField = document.createElement("input");
	idField.setAttribute("type", "hidden");
	idField.setAttribute("name", name);
	idField.setAttribute("value", id);

	form.appendChild(idField);

	if (id2 !== null && id2 !== "") {
		const idField2 = document.createElement("input");
		idField2.setAttribute("type", "hidden");
		idField2.setAttribute("name", "id2");
		idField2.setAttribute("value", id2);

		form.appendChild(idField2);
	}

	document.body.appendChild(form);

	form.submit();
}

/* Checks if all input forms have values in them. */
function validateForm() {
	const nodes = document.querySelectorAll("#form input[type=text]");

	for (let i = 0; i < nodes.length; i++) {
		if (nodes[i].value === "") {
			alert("Kaikissa kentissä pitää olla jotain.");

			return false;
		}
	}
}

/* Adds a cookie to indicate that the user has seen the disclaimer, and then removes the disclaimer. */
function processDisclaimer() {
	document.cookie = "disclaimer=true;path=/";
	document.getElementById("disclaimer").remove();

	return false;
}

/* Counts the characters used in the given field, and updates the text (innerHTML) of the status element. */
function countChars(field, pId) {
	const pElem = document.getElementById(pId);

	let color = "darkgreen";
	/* This is the color for a valid input. */
	let hintText = "";

	if (field.value.length < field.minLength) {
		color = "darkblue";
		/* The input is too short. */
		hintText = " (tarvitaan vähintään " + field.minLength + ")";
	} else if (field.value.length > field.maxLength) {
		color = "darkred";
		/* Now the input is too long. */
		hintText = " (voit käyttää enintään " + field.maxLength + ")";
	}

	pElem.innerHTML = "<span style='color: " + color + ";'>Merkkejä: " + field.value.length + "/" + field.maxLength + hintText + "</span>";
}

function loadAllConversations() {

	const xhttp = new XMLHttpRequest();

	let defaultConversation = undefined;

	if (window.location.hash) {
		defaultConversation = window.location.hash.replace('#', '');
	}

	xhttp.onreadystatechange = function () {
		if (this.readyState === 4 && this.status === 200) {
			const data = JSON.parse(this.responseText);

			const ul = document.getElementById("conversations");

			data.forEach(function (conversation) {

				if (defaultConversation === undefined) {
					defaultConversation = conversation["conversation_id"];
				}

				const li = document.createElement("li");

				li.classList.add("list-group-item");
				li.classList.add("list-group-item-action");
				li.classList.add("border-primary");
				li.setAttribute("role", "button");

				li.onclick = function () {
					loadSpecificConversation(conversation["conversation_id"]);
				};

				const span = document.createElement("span");
				span.setAttribute("class", "badge badge-primary badge-pill float-right mt-2");
				span.appendChild(document.createTextNode("5"));
				li.appendChild(span);

				const strong = document.createElement("strong");
				strong.classList.add("inline-text");
				strong.appendChild(document.createTextNode(conversation["other_profile"]));
				li.appendChild(strong);

				const p = document.createElement("p");
				p.classList.add("inline-text");
				p.appendChild(document.createTextNode(conversation["latest_message"]));
				li.appendChild(p);

				const date = new Date(conversation["date_created"]);
				let dateString = formatDate(date);

				const small = document.createElement("small");
				small.classList.add("inline-text");
				small.classList.add("text-muted");
				small.appendChild(document.createTextNode(dateString));
				li.appendChild(small);

				ul.appendChild(li);
			});

			loadSpecificConversation(defaultConversation);
		}
	};

	xhttp.open("GET", "conversations/all.json", true);
	xhttp.send();
}

function formatDate(datetime) {

	/* TODO: Compact this speedily-written code. */
	let string = "";

	const hours = datetime.getHours();
	if (hours.length === 1) {
		string += "0";
	}
	string += hours + ":";

	const minutes = datetime.getMinutes();
	if (minutes.length === 1) {
		string += "0";
	}
	string += minutes + ":";

	const seconds = datetime.getSeconds();
	if (seconds.length === 1) {
		string += "0";
	}
	string += seconds + " ";

	const days = datetime.getDate();
	if (days.length === 1) {
		string += "0";
	}
	string += days + ".";

	const months = datetime.getMonth();
	if (months.length === 1) {
		string += "0";
	}
	string += months + ".";

	string += datetime.getFullYear();

	return string;
}

function loadSpecificConversation(id) {
	let file, xhttp;
	const conversation = document.getElementById("conversation");

	/* Add the ID to the DIV. */

	// conversation.innerHTML = '<span class="text-muted">Ladataan keskustelua...</span>';

	file = "conversation/id/" + id;

	xhttp = new XMLHttpRequest();
	xhttp.onreadystatechange = function () {
		if (this.readyState === 4) {
			if (this.status === 200) {
				const data = JSON.parse(this.responseText);

				conversation.innerHTML = "";

				data.forEach(function (message) {
					const div = document.createElement("p");

					div.classList.add("message");

					const own_message = message["own_message"];
					if (own_message === true) {
						div.classList.add("float-right");
					} else {
						div.classList.add("float-left");
					}

					div.appendChild(document.createTextNode(message["content"]));
					conversation.appendChild(div);

					//history.pushState(null, null, "/conversation/id/" + id);
					window.location.hash = id;
				});
			}

			if (this.status === 404) {
				const p = document.createElement("p");
				p.appendChild(document.createTextNode("Keskustelua ei löytynyt. Oletko poistanut sen?"));
				conversation.innerHTML = p.innerHTML;
			}
		}

	};

	xhttp.open("GET", file, true);
	xhttp.send();
}

function getNewMessageCount() {
	let file, xhttp;
	const conversation = document.getElementById("conversation");

	file = "conversation/message_count.json";

	xhttp = new XMLHttpRequest();
	xhttp.onreadystatechange = function () {
		if (this.readyState === 4) {
			if (this.status === 200) {
				const data = JSON.parse(this.responseText)["count"];
				$("#message-count").html(data);
				$("#messages-no-new").hide();
				$("#messages-yes-new").removeClass("d-none");
			}
		}
	};

	xhttp.open("GET", file, true);
	xhttp.send();
}

function temp() {
	let form = $("#message-form");

	form.onsubmit = function (e) {

		e.preventDefault();

		let xhttp = new XMLHttpRequest();

		xhttp.onreadystatechange = function () {
			if (this.readyState === 4) {
				if (this.status === 201) {
					console.log(xhttp.responseText);
				}
			}
		};
		xhttp.open("POST", "/conversation/send", true);
		xhttp.setRequestHeader("Content-Type", "application/json");
		xhttp.send(JSON.stringify(e));
	};

}

function getBootstrapState() {
	/* This function returns the current breakpoint (Bootstrap). */

	const breakpoints = ["", "sm", "md", "lg", "xl"];

	let $dummy = $("<div>");
	$dummy.appendTo($("body"));

	for (let i = breakpoints.length - 1; i >= 0; i--) {

		const breakpoint = breakpoints[i];

		if (breakpoint === "") {
			$dummy.addClass("d-none");
		} else {
			$dummy.addClass("d-" + breakpoint + "-none");
		}

		if ($dummy.is(":hidden")) {

			$dummy.remove();

			if (breakpoint === "") {
				return "xs";
			} else {
				return breakpoint;
			}
		}
	}
	/* This should never happen. */

	console.log("No valid breakpoint found.");
	$dummy.remove();
}

function changeNavStyle(toCompact) {
	const nav = $("header .navbar");
	const div = nav.parent();

	if (toCompact) {
		nav.removeClass("rounded");
		nav.removeClass("mt-4");
		nav.removeClass("navbar-border-full");
		nav.addClass("navbar-border-bottom");
		div.removeClass("container");
	} else {
		nav.addClass("rounded");
		nav.addClass("mt-4");
		nav.addClass("navbar-border-full");
		nav.removeClass("navbar-border-bottom");
		div.addClass("container");
	}
}

function updateNavbar() {
	const breakpoint = getBootstrapState();
	if (breakpoint === "xs" || breakpoint === "sm") {
		changeNavStyle(true);
	} else {
		changeNavStyle(false);
	}
}