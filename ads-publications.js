async function loadAdsPublications() {
    const firstContainer = document.getElementById('first-author-publications');
    const otherContainer = document.getElementById('other-publications');
    const status = document.getElementById('ads-status');
    if (!firstContainer || !otherContainer || !status) return;

    status.textContent = 'Loading publications...';

    try {
        const [firstResponse, otherResponse] = await Promise.all([
            fetch('publications-cache-first-author.json'),
            fetch('publications-cache-other.json'),
        ]);

        if (!firstResponse.ok && !otherResponse.ok) {
            throw new Error('Could not load publication cache files. Run the preload script.');
        }

        const [firstData, otherData] = await Promise.all([
            firstResponse.ok ? firstResponse.json() : { response: { docs: [] } },
            otherResponse.ok ? otherResponse.json() : { response: { docs: [] } },
        ]);

        const firstDocs = firstData.response?.docs || [];
        const otherDocs = otherData.response?.docs || [];

        if (!firstDocs.length && !otherDocs.length) {
            status.textContent = 'No publications cached yet. Run: ADS_API_TOKEN=token python3 preload_publications.py';
            return;
        }

        firstContainer.innerHTML = firstDocs.length
            ? firstDocs.map(renderPublicationCard).join('')
            : '<div class="card"><p>No first-author publications have been cached yet.</p></div>';

        otherContainer.innerHTML = otherDocs.length
            ? otherDocs.map(renderPublicationCard).join('')
            : '<div class="card"><p>No other publications have been cached yet.</p></div>';

        status.textContent = '';
    } catch (error) {
        status.textContent = `Unable to load publications: ${error.message}`;
        firstContainer.innerHTML = '';
        otherContainer.innerHTML = '';
        console.error('Publication load error:', error);
    }
}

function renderPublicationCard(doc) {
    const title = Array.isArray(doc.title) ? doc.title[0] : doc.title || 'Untitled';
    const authors = Array.isArray(doc.author)
        ? doc.author.slice(0, 3).join(', ') + (doc.author.length > 3 ? ', et al.' : '')
        : doc.author || 'Unknown authors';
    const pub = doc.pub || 'Publication details unavailable';
    const year = doc.year || '';
    const abstractText = doc.abstract ? (Array.isArray(doc.abstract) ? doc.abstract[0] : doc.abstract) : '';
    const abstract = abstractText ? `${abstractText.slice(0, 180).replace(/\s+$/, '')}...` : '';
    const link = doc.bibcode ? `https://ui.adsabs.harvard.edu/abs/${doc.bibcode}` : '#';

    return `
        <div class="card">
            <h3>${title}</h3>
            <p><strong>${authors}</strong></p>
            <p>${pub}${year ? ` • ${year}` : ''}</p>
            ${abstract ? `<p>${abstract}</p>` : ''}
            ${doc.bibcode ? `<a class="button button-secondary" href="${link}" target="_blank" rel="noopener">View on ADS</a>` : ''}
        </div>
    `;
}

window.addEventListener('load', loadAdsPublications);
