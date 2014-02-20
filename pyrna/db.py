import os, shutil, subprocess, re, urllib, urllib2
from pandas import DataFrame
from pyrna.features import RNA
from bs4 import BeautifulSoup
import parsers, utils

class PDBQuery:
    """
    A utility class to use the method query from the PDB class (see PDB class in module pyrna.db).
    """
    def __init__(self, min_res = '0.1', max_res = '3.0', min_date = None, max_date = None, keywords = [], authors = [], pdb_ids = [], title_contains = [], contains_rna = 'Y', contains_protein = 'Y', contains_dna = 'N', contains_hybrid = 'N', experimental_method = 'X-RAY'):
        self.min_res = min_res
        self.max_res = max_res
        self.min_date = min_date
        self.max_date = max_date
        self.keywords = keywords
        self.authors = authors
        self.pdb_ids = pdb_ids
        self.title_contains = title_contains
        self.contains_rna = contains_rna
        self.contains_protein = contains_protein
        self.contains_dna = contains_dna
        self.contains_hybrid = contains_hybrid
        self.experimental_method = experimental_method
        

class PDB:
    """
    Wrapper for the PDB database http://www.rcsb.org/
    """

    def __init__(self):
        pass

    def get_entry(self, pdb_id):
        """
        Return the content of a PDB entry as a string
        """
        response = urllib.urlopen("http://www.rcsb.org/pdb/download/downloadFile.do?fileFormat=pdb&compression=NO&structureId=%s"%pdb_id)
        content = str(response.read())
        return content

    def query(self, query):
        """
        Returns a list of PDB ids in answer to the query

        Parameters:
        - query: the query as a PDBQuery object

        Returns:
        - a list of pdb ids
        """
        min_res = query.min_res or '0.1'
        max_res = query.max_res or '3.0'
        min_date = query.min_date or None
        max_date = query.max_date or None
        keywords = query.keywords or []
        authors = query.authors or []
        pdb_ids = query.pdb_ids or []
        title_contains = query.title_contains or []
        contains_rna = query.contains_rna or 'Y'
        contains_protein = query.contains_protein or 'Y'
        contains_dna = query.contains_dna or 'N'
        contains_hybrid = query.contains_hybrid or 'N'
        experimental_method = query.experimental_method or 'X-RAY'
        post_data = '<?xml version="1.0" encoding="UTF-8"?><orgPdbCompositeQuery version="1.0">'
        ids = []
        refinementLevel = 0

        if experimental_method == 'X-RAY' and (max_res or min_res):
            if refinementLevel:
                post_data += '<queryRefinement><queryRefinementLevel>'+str(refinementLevel)+'</queryRefinementLevel><conjunctionType>and</conjunctionType>'
            else:
                post_data += '<queryRefinement><queryRefinementLevel>'+str(refinementLevel)+'</queryRefinementLevel>'   
            post_data += '\
<orgPdbQuery>\
<version>head</version>\
<queryType>org.pdb.query.simple.ResolutionQuery</queryType>\
<description>Resolution query</description>\
<refine.ls_d_res_high.comparator>between</refine.ls_d_res_high.comparator>'

            if min_res:
                post_data += '\
<refine.ls_d_res_high.min>'+min_res+'</refine.ls_d_res_high.min>'                   
            
            if max_res:
                post_data += '\
<refine.ls_d_res_high.max>'+max_res+'</refine.ls_d_res_high.max>'

            post_data += '</orgPdbQuery></queryRefinement>'
            refinementLevel += 1

        if max_date or min_date:
            if refinementLevel:
                post_data += '<queryRefinement><queryRefinementLevel>'+str(refinementLevel)+'</queryRefinementLevel><conjunctionType>and</conjunctionType>'
            else:
                post_data += '<queryRefinement><queryRefinementLevel>'+str(refinementLevel)+'</queryRefinementLevel>'   
            
            post_data +='\
<orgPdbQuery>\
<version>head</version>\
<queryType>org.pdb.query.simple.ReleaseDateQuery</queryType>\
<description>Release Date query</description>\
<refine.ls_d_res_high.comparator>between</refine.ls_d_res_high.comparator>'
            
            if min_date:
                post_data += '\
<database_PDB_rev.date.min>'+min_date+'</database_PDB_rev.date.min>'                   
            
            if max_date:
                post_data += '\
<database_PDB_rev.date.max>'+max_date+'</database_PDB_rev.date.max>'
            
            post_data += '</orgPdbQuery></queryRefinement>'
            refinementLevel += 1

        for i in range(0, len(title_contains)):
            titleContain = title_contains[i]
            if refinementLevel:
                post_data += '<queryRefinement><queryRefinementLevel>'+str(refinementLevel)+'</queryRefinementLevel><conjunctionType>and</conjunctionType>'
            else:
                post_data += '<queryRefinement><queryRefinementLevel>'+str(refinementLevel)+'</queryRefinementLevel>'   
            post_data += '\
<orgPdbQuery>\
<version>head</version>\
<queryType>org.pdb.query.simple.StructTitleQuery</queryType>\
<description>StructTitleQuery: struct.title.comparator=contains struct.title.value='+titleContain+'</description>\
<struct.title.comparator>contains</struct.title.comparator>\
<struct.title.value>'+titleContain+'</struct.title.value>\
</orgPdbQuery></queryRefinement>'
            refinementLevel += 1

        if keywords:
            if refinementLevel:
                post_data += '<queryRefinement><queryRefinementLevel>'+str(refinementLevel)+'</queryRefinementLevel><conjunctionType>and</conjunctionType>'
            else:
                post_data += '<queryRefinement><queryRefinementLevel>'+str(refinementLevel)+'</queryRefinementLevel>'   
            post_data += '\
<orgPdbQuery>\
<version>head</version>\
<queryType>org.pdb.query.simple.AdvancedKeywordQuery</queryType>\
<description>Text Search for: '+" ".join(keywords)+'</description>\
<keywords>'+" ".join(keywords)+'</keywords>\
</orgPdbQuery></queryRefinement>'
            refinementLevel += 1

        if pdb_ids:
            if refinementLevel:
                post_data += '<queryRefinement><queryRefinementLevel>'+str(refinementLevel)+'</queryRefinementLevel><conjunctionType>and</conjunctionType>'
            else:
                post_data += '<queryRefinement><queryRefinementLevel>'+str(refinementLevel)+'</queryRefinementLevel>'   
            
            post_data += '\
<orgPdbQuery>\
<version>head</version>\
<queryType>org.pdb.query.simple.StructureIdQuery</queryType>\
<description>Simple query for a list of PDB IDs ('+str(len(pdb_ids))+' IDs) :'+", ".join(pdb_ids)+'</description>\
<structureIdList>'+", ".join(pdb_ids)+'</structureIdList>\
</orgPdbQuery></queryRefinement>'
            refinementLevel += 1

        if experimental_method:
            if refinementLevel:
                post_data += '<queryRefinement><queryRefinementLevel>'+str(refinementLevel)+'</queryRefinementLevel><conjunctionType>and</conjunctionType>'
            else:
                post_data += '<queryRefinement><queryRefinementLevel>'+str(refinementLevel)+'</queryRefinementLevel>'   
            
            post_data += '\
<orgPdbQuery>\
<version>head</version>\
<queryType>org.pdb.query.simple.ExpTypeQuery</queryType>\
<description>Experimental Method is '+experimental_method+'</description>\
<mvStructure.expMethod.value>'+experimental_method+'</mvStructure.expMethod.value>\
</orgPdbQuery></queryRefinement>'
            refinementLevel += 1

        for i in range(0, len(authors)):
            author = authors[i]
            if refinementLevel:
                post_data += '<queryRefinement><queryRefinementLevel>'+str(refinementLevel)+'</queryRefinementLevel><conjunctionType>and</conjunctionType>'
            else:
                post_data += '<queryRefinement><queryRefinementLevel>'+str(refinementLevel)+'</queryRefinementLevel>'   
            
            post_data += '\
<orgPdbQuery>\
<version>head</version>\
<queryType>org.pdb.query.simple.AdvancedAuthorQuery</queryType>\
<description>Author Search: Author Search: audit_author.name='+author+' OR (citation_author.name='+author+' AND citation_author.citation_id=primary)</description>\
<exactMatch>false</exactMatch>\
<audit_author.name>'+author+'</audit_author.name>\
</orgPdbQuery></queryRefinement>'
            refinementLevel += 1

        #chain type
        if refinementLevel:
            post_data += '<queryRefinement><queryRefinementLevel>'+str(refinementLevel)+'</queryRefinementLevel><conjunctionType>and</conjunctionType>'
        else:
            post_data += '<queryRefinement><queryRefinementLevel>'+str(refinementLevel)+'</queryRefinementLevel>'   
        
        post_data += '\
<orgPdbQuery>\
<version>head</version>\
<queryType>org.pdb.query.simple.ChainTypeQuery</queryType>\
<description>Chain Type</description>\
<contains_protein>'+contains_protein+'</contains_protein>\
<contains_dna>'+contains_dna+'</contains_dna>\
<contains_rna>'+contains_rna+'</contains_rna>\
<contains_hybrid>'+contains_hybrid+'</contains_hybrid>\
</orgPdbQuery></queryRefinement>'
        refinementLevel += 1

        post_data += '</orgPdbCompositeQuery>'

        import urllib2

        req =  urllib2.Request("http://www.rcsb.org/pdb/rest/search", data = post_data)

        f = urllib2.urlopen(req)
        
        result = f.read()

        if result:
           ids = result.split('\n')[:-1]
        
        return ids

class NCBI:
    """
    Wrapper for the NCBI database
    """

    def __init__(self, cache_dir="/tmp/NCBI"):
        self.cache_dir = cache_dir
        if not os.path.exists(self.cache_dir):
            shutil.os.mkdir(self.cache_dir)
        self._eutils_base_url = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/"

    def get_CDD_data(self):
        if os.path.exists(self.cache_dir+'/CDD/'):
            shutil.rmtree(self.cache_dir+'/CDD/')
        shutil.os.mkdir(self.cache_dir+'/CDD/')
        subprocess.call([os.path.dirname(os.path.realpath(__file__))+"/../files/scripts/shell/getCDD.sh %s ftp://ftp.ncbi.nih.gov/pub/mmdb/cdd/cdd.tar.gz"%self.cache_dir+'/CDD/'], shell=True)

    def get_assembled_fungi_species(self):
        import ftplib
        ftp = ftplib.FTP("ftp.ncbi.nlm.nih.gov")
        ftp.login()
        species = []
        entries = ftp.nlst('genomes/ASSEMBLY_REPORTS/Eukaryotes/fungi/')
        entries.sort()
        for species_dir in entries:
            species.append(' '.join(species_dir.split('/')[-1].split('_')))
        return species

    def efetch(self, db, ids, rettype = None, header = None):
        """
        Wrapper for the Efetch Entrez Utilities
        """
        if rettype:
            response = urllib.urlopen("%sefetch.fcgi?db=%s&id=%s&rettype=%s"%(self._eutils_base_url, db, ','.join(ids), rettype))
        else:
            response = urllib.urlopen("%sefetch.fcgi?db=%s&id=%s"%(self._eutils_base_url, db, ','.join(ids)))
        if header:
            content = str(response.read(header))
        else:
            content = str(response.read())
        response.close()
        return content

    def esearch(self, db, term, retstart = 0, retmax = 20):
        """
        Wrapper for the Esearch Entrez Utilities
        """
        response = urllib.urlopen("%sesearch.fcgi?db=%s&term=%s&retstart=%i&retmax=%i"%(self._eutils_base_url, db, term, retstart, retmax))
        content = str(response.read())
        response.close()
        return content

    def esummary(self, db, ids, retstart = 0, retmax = 20):
        """
        Wrapper for the Esummary Entrez Utilities
        """
        if len(ids) < 200:
            response = urllib.urlopen("%sesummary.fcgi?db=%s&id=%s&retstart=%i&retmax=%i"%(self._eutils_base_url, db, ','.join(ids), retstart, retmax))
            content = str(response.read())
            response.close()
            return content
        else:
            data = {
                'db':db,
                'id':','.join(ids)
            }
            data = urllib.urlencode(data) 
            req = urllib2.Request("%sesummary.fcgi"%self._eutils_base_url, data)
            response = urllib2.urlopen(req)
            content = str(response.read())
            response.close()
            return content

    def elink(self, db, dbfrom, id):
        """
        Wrapper for the Elink Entrez Utilities
        """
        response = urllib.urlopen("%selink.fcgi?db=%s&dbfrom=%s&id=%s"%(self._eutils_base_url, db, dbfrom, id))
        content = str(response.read())
        response.close()
        return content

class RNA3DHub:

    """
    Wrapper for the RNA3DHub database (http://rna.bgsu.edu/rna3dhub/)
    """

    def __init__(self, release="current"):
        self.release = release

    def get_clusters(self, resolution=2.5):
        """
        Returns the clusters of solved 3Ds from the non-redundant list provided by http://rna.bgsu.edu/rna3dhub/nrlist

        Parameters:
        -resolution: Default value is 2.5

        A pandas DataFrame whose columns are:
        - the cluster id
        - the list of pdb ids
        """
        rows = []
        response = urllib.urlopen("http://rna.bgsu.edu/rna3dhub/nrlist/download/"+str(self.release)+"/"+str(resolution)+"A/csv")
        content = str(response.read())
        for line in content.split('\n'):
            if len(line.strip()) > 0:
                tokens = line.split(',')
                pdb_ids = ' '.join(tokens[1:])
                rows.append([re.sub('"', '', tokens[0]), re.sub('"', '', pdb_ids).split(' ')]);
        return DataFrame(rows, columns=['cluster-id', 'pdb-ids'])

class Rfam:

    """
    Wrapper for the Rfam database (http://rfam.sanger.ac.uk/)
    """

    """
    Parameters:
    -----------
    - use_website : if False, data will be downloaded from the FTP of Rfam. If True, data will be downloaded from the website using URLs (default: False).
    - cache_dir (default: None): the directory used to cache data if download from the FTP. If None, the wrapper will use /tmp/RFAM_${random_name} 
    - version: the version of Rfam to be used. If data are downloaded from the website, this parameter is not used and only the CURRENT version will be used.
    """
    def __init__(self, use_website = False, cache_dir = None, version = 'CURRENT'):
        self.base_url = "http://rfam.sanger.ac.uk/"
        self.use_website = use_website
        if not cache_dir:
            self.cache_dir = "/tmp/RFAM_%s"%utils.generate_random_name(7)
        else:
            self.cache_dir = cache_dir
        self.version = version
        if not os.path.exists(self.cache_dir):
            shutil.os.mkdir(self.cache_dir)

    """
    This method returns the contents for an Rfam Entry

    Parameters:
    -----------
    - rfam_id: the id of the Rfam family
    - aln_type (default: 'seed'): the type of alignment. Can be equal to 'seed' or 'full'.
    - nse_labels (default: 0): 0 to have organism names and 1 to have accession numbers/start-end. If equal to 1, the dict returned  in the tuple will be empty.
    - format (default: None): the format of the data returned. Can beequal to 'stockholm', 'fasta' or None. 

    Returns:
    --------
    Depends on the value of the parameter format. If equal to: 
    - None: returns a tuple like (list of aligned sequences, dict of organism names (keys) and accession numbers/start-end (values), pandas Dataframe listing base-pairs).
    - "stockholm": returns the raw data with the stockholm format (as a String).
    - "fasta": returns the raw data with the fasta format (as a String).
    """
    def get_entry(self, rfam_id, aln_type = 'seed', nse_labels = 0, format = None):

        content = None

        if self.use_website:
            response = urllib.urlopen("%s/family/%s/alignment?acc=%s&alnType=%s&nseLabels=%i&format=stockholm&download=1"%(self.base_url, rfam_id, rfam_id, aln_type, nse_labels))
            content = str(response.read())
            response.close()
            if not content.startswith("# STOCKHOLM"):
                raise Exception("Rfam family %s not found!!"%rfam_id)            
        else:
            path = os.path.join(self.cache_dir, aln_type, "%s.sto"%rfam_id)

            if not os.path.exists(path):
                raise Exception("file %s not found!!"%path)        
            else:
                h = open(path, 'r')
                content = h.read()
                h.close()
                if not content.strip().split('\n')[-1].strip() == '//': #incomplete file
                    raise Exception("file %s is incomplete!!"%path)    

        if not format:
            return parsers.parse_stockholm(content)
        elif format == 'stockholm':
            return content
        elif format == 'fasta':
            (rnas, organisms, consensus2D) = parsers.parse_stockholm(content)
            return parsers.to_fasta(rnas)

    """
    This method returns the consensus sequence for an Rfam Entry

    Parameters:
    ---------
    - rfam_id: the id of the Rfam family

    Returns:
    --------
    The consensus sequence as an RNA object (see pyrna.features). 
    Returns None if no consensus sequence found.
    """
    def get_consensus_sequence(self, rfam_id):
        consensus_seq = []
        for line in self.get_entry(rfam_id, format='stockholm').split('\n'):
            if line.startswith("#=GC RF"):
                consensus_seq.append(line.split("#=GC RF")[1].strip().replace('.','').replace('-','').replace('~','').upper())
        if len(consensus_seq):
            return RNA(name = 'consensus sequence for %s'%rfam_id, sequence  = ''.join(consensus_seq))
        else:
            return None

    def get_families_details(self):
        """
        This method returns details for each RFAM family.

        Returns:
        ------
        A pandas DataFrame whose columns are:
        - id
        - accession (RFXXXXX)
        - family
        - description
        - number of sequences in the seed alignment
        - number of sequences in the full alignment
        """
        if os.path.exists(self.cache_dir+'/rfam.txt'):
            shutil.os.remove(self.cache_dir+'/rfam.txt')
        familiesDetails = []
        subprocess.call([os.path.dirname(os.path.realpath(__file__))+"/../files/scripts/shell/getRfam_families.sh "+self.cache_dir+" "+self.version], shell=True)
        f = open(self.cache_dir+'/rfam.txt')
        lines = f.readlines()
        for line in lines:
            rfam_family = {}
            familiesDetails.append(rfam_family)
            tokens = line.split('\t')
            rfam_family['id'] = tokens[3]
            rfam_family['accession'] = tokens[2]
            rfam_family['family'] = re.sub(';',',', re.sub(';$','',tokens[18])).strip()
            rfam_family['description'] = tokens[4]
            rfam_family['seed'] = tokens[16]
            rfam_family['full'] = tokens[17]
        f.close()
        return DataFrame(familiesDetails)

    def get_families_with_structures(self):
        """
        This method returns details for each RFAM family linked to at least one PDB structure

        Returns:
        ------
        A pandas DataFrame whose columns are:
        - rfam_id (RFXXXXX)
        - pdb_id
        - chain_name
        - 3d_start
        - 3d_end
        - ncbi_id
        - ncbi_start
        - ncbi_end
        """
        rfam_families_with_3Ds = {}
        #first we're using the file rfam.txt from the RFAM FTP to get the correspondance between the RFAM ID and the database ID (the file pdb_rfam_reg.txt is using the database ID instead of the RFAM ID)
        if os.path.exists(self.cache_dir+'/rfam.txt'):
            shutil.os.remove(self.cache_dir+'/rfam.txt')
        database_ids_2_rfam_ids = {}
        subprocess.call([os.path.dirname(os.path.realpath(__file__))+"/../files/scripts/shell/getRfam_families.sh "+self.cache_dir+" "+self.version], shell=True)
        f = open(self.cache_dir+'/rfam.txt')
        lines = f.readlines()
        for line in lines:
            tokens = line.split('\t')
            database_ids_2_rfam_ids[tokens[0]] = tokens[2]
        f.close()
        f = open(self.cache_dir+'/pdb_rfam_reg.txt')
        lines = f.readlines()
        for line in lines:
            rfam_family = {}
            tokens = line.split('\t')
            rfam_accession = database_ids_2_rfam_ids[tokens[1]]
            rfam_family['pdb_id'] = tokens[2]
            rfam_family['chain_name'] = tokens[3]
            rfam_family['3d_start'] = tokens[4]
            rfam_family['3d_end'] = tokens[5]
            rfam_family['ncbi_id'] = tokens[6]
            rfam_family['ncbi_start'] = tokens[7]
            rfam_family['ncbi_end'] = tokens[8]
            if not rfam_families_with_3Ds.has_key(rfam_accession):
                rfam_families_with_3Ds[rfam_accession] = []    
            rfam_families_with_3Ds[rfam_accession].append(rfam_family)       
        f.close()
        return rfam_families_with_3Ds

    def get_genomic_entries(self):
        """
        Return all the details of the genomes handled by RFAM.

        Returns :
        -------
        A pandas Dataframe whose columns are:
        - accession number
        - name of the organism
        - lineage of the organism
        """
        organisms = []
        if os.path.exists(self.cache_dir+'/genome_entry.txt'):
            shutil.os.remove(self.cache_dir+'/genome_entry.txt')
        subprocess.call([os.path.dirname(os.path.realpath(__file__))+"/../files/scripts/shell/getRfam_genomicEntries.sh "+self.cache_dir+" ftp://ftp.sanger.ac.uk/pub/databases/Rfam/"+self.version+"/database_files/genome_entry.txt.gz"], shell=True)
        f = open(self.cache_dir+'/genome_entry.txt')
        lines = f.readlines()
        for line in lines:
            tokens = line.split('\t')
            organism = {}
            organism['accession'] = tokens[1]
            organism['name'] = tokens[3]
            organism['lineage'] = tokens[5]
            organisms.append(organism)
        return DataFrame(organisms)

    def generate_seed_alignments(self):
        """
        This method has to be called if the Rfam wrapper uses data from the FTP. Seed alignments will be downloaded and stored locally.
        """
        if not os.path.exists(self.cache_dir+'/seed/Rfam.seed'):
            if os.path.exists(self.cache_dir+'/seed/'):
                shutil.rmtree(self.cache_dir+'/seed/')
            shutil.os.mkdir(self.cache_dir+'/seed/')
            subprocess.call([os.path.dirname(os.path.realpath(__file__))+"/../files/scripts/shell/getRfam_data.sh "+self.cache_dir+"/seed/ ftp://ftp.sanger.ac.uk/pub/databases/Rfam/"+self.version+"/ Rfam.seed.gz"], shell=True)
        f = open(self.cache_dir+'/seed/Rfam.seed')
        lines = f.readlines()
        currentAccession = None
        currentContent = None

        for line in lines:
            if re.match('^#=GF AC', line):
                if currentContent and currentAccession:
                    output = open(self.cache_dir+'/seed/'+currentAccession+'.sto', 'w')
                    output.write(currentContent)
                    output.close()    
                currentContent = "# STOCKHOLM 1.0\n"
                currentContent += line
                currentAccession = re.split("\s+", line)[-2]
            elif currentContent and not re.match('^# STOCKHOLM 1.0', line):
                currentContent += line

        if currentContent and currentAccession:
            output = open(self.cache_dir+'/seed/'+currentAccession+'.sto', 'w')
            output.write(currentContent)
            output.close()
                            
        f.close()    
               
    def generate_full_alignments(self):
        """
        This method has to be called if the Rfam wrapper uses data from the FTP. Full alignments will be downloaded and stored locally.
        """
        if not os.path.exists(self.cache_dir+'/full/Rfam.full'):
            if os.path.exists(self.cache_dir+'/full/'):
                shutil.rmtree(self.cache_dir+'/fulls')
            shutil.os.mkdir(self.cache_dir+'/full/')
            subprocess.call([os.path.dirname(os.path.realpath(__file__))+"/../files/scripts/shell/getRfam_data.sh "+self.cache_dir+"/full/ ftp://ftp.sanger.ac.uk/pub/databases/Rfam/"+self.version+"/ Rfam.full.gz"], shell=True)
        f = open(self.cache_dir+'/full/Rfam.full')
        lines = f.readlines()
        currentAccession = None
        currentContent = None

        for line in lines:
            if re.match('^#=GF AC', line):
                if currentContent and currentAccession:
                    output = open(self.cache_dir+'/full/'+currentAccession+'.sto', 'w')
                    output.write(currentContent)
                    output.close()    
                currentContent = "# STOCKHOLM 1.0\n"
                currentContent += line
                currentAccession = re.split("\s+", line)[-2]
            elif currentContent and not re.match('^# STOCKHOLM 1.0', line):
                currentContent += line

        if currentContent and currentAccession:
            output = open(self.cache_dir+'/full/'+currentAccession+'.sto', 'w')
            output.write(currentContent)
            output.close()
                            
        f.close()

    def generate_CMs(self):
        """
        This method has to be called if you plan to use cmsearch (see pyrna.computations). The covariance models will be downloaded and stored locally.
        """
        if not os.path.exists(self.cache_dir+'/CMs/Rfam.cm'):
            if os.path.exists(self.cache_dir+'/CMs/'):
                shutil.rmtree(self.cache_dir+'/CMs/')
            shutil.os.mkdir(self.cache_dir+'/CMs/')
            subprocess.call([os.path.dirname(os.path.realpath(__file__))+"/../files/scripts/shell/getRfam_data.sh "+self.cache_dir+"/CMs/ ftp://ftp.sanger.ac.uk/pub/databases/Rfam/"+self.version+"/ Rfam.cm.gz"], shell=True)
        f = open(self.cache_dir+'/CMs/Rfam.cm')
        lines = f.readlines()

        familyName = None
        rfamHeader = None
        families = {}
        currentAccession = None
        currentContent = None

        for line in lines:
            if re.match('/^\/\//', line) and currentContent :
                currentContent += line
            elif re.match('^INFERNAL', line):
                rfamHeader = line    
            elif re.match('^NAME', line):
                familyName = line
                if currentContent:
                    families[currentAccession] = currentContent;
                    currentContent = None;
            elif re.match('^ACC', line):
                if line.startswith("ACCESSION"):
                    currentAccession = line.split("ACCESSION")[1].strip()
                else:    
                    currentAccession = line.split("ACC")[1].strip()
                currentContent = ""
                currentContent += rfamHeader
                currentContent += familyName
                currentContent += line
            elif currentContent:
                currentContent += line
        f.close()

        if currentContent:
            families[currentAccession] = currentContent;
        
        for key in families.keys():
            f = open(self.cache_dir+'/CMs/'+key+'.cm', 'w')
            f.write(families[key])
            f.close()