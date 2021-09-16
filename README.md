# Bepress Plugin for Janeway

This plugin allows you to import an export of a bepress Digital Commons publication into a Janeway instance

There are 3 supported [Digital Commons structure types](https://bepress.com/reference_guide_dc/digital-commons-structures/):
- Journals
- Series (Imported as a journal)
- Events (Limited support)

## Installation Instructions
1. Clone this repository into the Janeway plugins folder (`path/to/janeway/src/plugins/`)
2. Run the plugin installation command: `python3 src/manage.py install_plugins typesetting`.
3. Run the migration command `python3 src/manage.py migrate bepress`
4. Restart your webserver

## Usage guide
Bepress offers various mechanisms for exporting your metadata:

### Importing from an Amazon S3 backup
If you have enabled the Amazon S3 backup service with Bepress, you will have access to a backup containing your articles files and metadata in XML format. In order to ingest that backup into Janeway, you will need to load that backup directory into Janeway's file system under `src/files/plugins/bepress`.

### Importing from a spreadhseet
If you don't have access to a bepress archive via Amazon S3, you can instead download a [batch export](https://bepress.com/reference_guide_dc/batch-upload-export-revise/) from your bepress installation.
The metadata is not as complete as with an XML archive (e.g submission dates are not present) But it has enough metadata to recreate the articles in Janeway.

__Note__
Some exports won't include the PDF URL (`fulltext_url`), in those cases, this plugin will attempt to retrieve the URL of the PDF from the live article page.

The spreadsheet needs to be exported as a CSV before you can import it into Janeway and then it be loaded from the Bepress plugin page in your Janeway installation. Janeway will generate a set of XML files, equivalent to the bepress archive format that will be saved under `src/files/plugins/bepress`

### Metadata Bindings
You can see a table on how the metadata is translated from the Bepress archives into Janeway in [this document](docs/data_mappings.md)


### Running the import process
Once your XML metadata has been loaded in (whether from an archive or from a CSV), you can run the import process by visiting the Bepress page in your Janeway installation and completing the import form.
In this form you will need to select the journal onto which you want to load the articles, the structure type of the incoming data in bepress as well as an option to load the content onto a different Issue in Janeway than the issue declared on the article metadata:
![Bepress Import Form](bepress_import.png?raw=true "Bepress Import Form")

