# containers_classic

class Layout():
    def copy(self):
        l2 = Layout(self.num_symbols, self.args)
        l2.containers = self.containers.copy()
        l2.container_types = self.container_types.copy()
        l2.addr_to_container_ids = self.addr_to_container_ids.copy()
        return l2

    def __init__(self, num_symbols, args):
        self.args = args
        self.num_symbols = num_symbols
        self.area = self.num_symbols * self.num_symbols
        self.blocksPerRow = 3
        self.bw = 3
        self.bh = 3
        self.ptype = args.puzzle_type
        self.containers = []
        self.container_types = []
        # rows
        for y in range(self.num_symbols):
            cont = [y*self.num_symbols + x for x in range(self.num_symbols)]
            self.containers.append(cont)
            self.container_types.append('row')
        # cols
        for x in range(self.num_symbols):
            cont = [y*self.num_symbols + x for y in range(self.num_symbols)]
            self.containers.append(cont)
            self.container_types.append('col')
        # blocks
        for bi in range(self.num_symbols):
            (ox,oy) = ((bi%self.blocksPerRow) * self.bw, (bi//self.blocksPerRow) * self.bh)
            cont = [(oy+i//self.bw)*self.num_symbols+(ox+i%self.bw) for i in range(self.num_symbols)]
            self.containers.append(cont)
            self.container_types.append('block')

        self.compute_addr_to_container_ids()

    def compute_addr_to_container_ids(self):
        self.addr_to_container_ids = []
        for addr in range(self.area):
            self.addr_to_container_ids.append(self.get_container_ids_for_addr(addr))
        self.organize_containers_by_type()


    def get_container_ids_for_addr(self, addr):
        # return a list of container ids for all containers which contain this digit
        container_ids = []
        for ci,cont in enumerate(self.containers):
            if addr in cont:
                container_ids.append(ci)
        return container_ids


    def add_diagonals(self):
        # add additional container for the two diagonals
        contBackslash = [xy*self.num_symbols + xy for xy in range(self.num_symbols)]
        contSlash = [xy*self.num_symbols + (self.num_symbols-1)-xy for xy in range(self.num_symbols)]
        self.containers.append(contBackslash)
        self.container_types.append('backslash')
        self.containers.append(contSlash)
        self.container_types.append('slash')
        self.compute_addr_to_container_ids()
        self.ptype += "-diag"

    def add_windows(self):
        # add additional container for the two diagonals
        window_conts = [[10,11,12,19,20,21,28,29,30],
                        [14,15,16,23,24,25,32,33,34],
                        [46,47,48,55,56,57,64,65,66],
                        [50,51,52,59,60,61,68,69,70],
                        [1,2,3,37,38,39,73,74,75],
                        [5,6,7,41,42,43,77,78,79],
                        [9,18,27,13,22,31,17,26,35],
                        [45,54,63,49,58,67,53,62,71],
                        [0,4,8,36,40,44,72,76,80]]
        for cont in window_conts:
            self.containers.append(cont)
            self.container_types.append('window')
        # for gy in range(2):
        #     for gx in range(2):
        #         contWindow = [(1+gy*4+y)*self.num_symbols + (1+gx*4+x) for x in range(3) for y in range(3)]
        #         self.containers.append(contWindow)
        #         self.container_types.append('window')
        self.compute_addr_to_container_ids()
        self.ptype += "-windows"

    def add_centerdots(self):
        # add additional container for the two diagonals
        contDots = [(1+y*3)*self.num_symbols + (1+x*3) for x in range(3) for y in range(3)]
        self.containers.append(contDots)
        self.container_types.append('centerdot')
        self.compute_addr_to_container_ids()
        self.ptype += "-centerdot"


    def get_prefix(self):
        return self.ptype
    
    def organize_containers_by_type(self):
        # produce a list of records grouped by type, each record contains the type name, and the list of container_ids that have that type
        self.containers_by_type = []
        unique_types = list(set(self.container_types))
        for ct in unique_types:
            type_cids = [ci for ci,ct2 in enumerate(self.container_types) if ct2 == ct]
            self.containers_by_type.append({'type':ct, 'cids':type_cids})

    def draw_layout(self, draw, draw_dimensions):
        lm,tm,gw,gh,cw,ch = draw_dimensions['lm'],draw_dimensions['tm'],draw_dimensions['gw'],draw_dimensions['gh'],draw_dimensions['cw'],draw_dimensions['ch']
        for y in range(0,self.num_symbols+1,3):
            draw.line((lm,tm+y*ch,lm+gw*cw,tm+y*ch),fill='black',width=4)
        for x in range(0,self.num_symbols+1,3):
            draw.line((lm+x*cw,tm,lm+x*cw,tm+gh*ch),fill='black',width=4)
