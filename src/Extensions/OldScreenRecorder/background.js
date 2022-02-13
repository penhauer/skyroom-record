chrome.runtime.onMessage.addListener((message, sender) => {
	const { type } = message;
	switch (type) {
		case 'RECORDING_STOPPED':
			chrome.windows.update(sender.tab.windowId, { focused: true });
	}
});

chrome.browserAction.onClicked.addListener(() => {
	const width = 800;
	const height = 690;
	const top = Math.round((window.screen.availHeight - height) / 2);
	const left = Math.round((window.screen.availWidth - width) / 2);
	chrome.windows.create({
		url: chrome.extension.getURL('index.html'),
		width,
		height,
		top,
		left,
		type: 'popup',
	});
})

chrome.runtime.onUpdateAvailable.addListener(e => {
	console.log('Disable automatic update')
})
