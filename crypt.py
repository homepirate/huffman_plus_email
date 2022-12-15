import math


class Node:

    def __init__(self, name=None, value=None):
        self.name = name
        self.value = value
        self.right_child = None
        self.left_child = None

    def __repr__(self):
        return f'{self.name=} {self.value=}'


class Tree:

    def __init__(self, chars_count, text):
        self.original_text = text
        self.Leaf = [Node(n, v) for n, v in chars_count.items()]
        while len(self.Leaf) != 1:
            self.Leaf.sort(key=lambda x: x.value, reverse=True)
            n = Node(value=(self.Leaf[-1].value + self.Leaf[-2].value))
            n.right_child = self.Leaf.pop()
            n.left_child = self.Leaf.pop()
            self.Leaf.append(n)
        self.root = self.Leaf[0]
        self.Buffer = list(range(10))
        self.char_coded = dict()

    def encrypt_char(self, tree, length):
        code = ""
        if not tree:
            return
        elif tree.name:
            for i in range(length):
                code += str(self.Buffer[i])
            self.char_coded.update({tree.name: code})
            return
        self.Buffer[length] = 0
        self.encrypt_char(tree.right_child, length + 1)
        self.Buffer[length] = 1
        self.encrypt_char(tree.left_child, length + 1)

    def get_code(self):
        self.encrypt_char(self.root, 0)

    def encrypt(self):
        new_str = ""
        for i in self.original_text:
            new_str += self.char_coded[i]
        return new_str

    @staticmethod
    def decrypt(word, char_order):
        new_str_array = []
        char = ""
        for i in word:
            char += i
            for i in char_order:
                if char_order[i] == char:
                    new_str_array.append(i)
                    char = ""
                    break
        return "".join(new_str_array)





def main():
    word = input()
    dict_count = {i: word.count(i) for i in set(word)}
    dict_count = dict(sorted(dict_count.items(), key=lambda x: x[1], reverse=True))
    dict_count_frequency = {i:[word.count(i), round(word.count(i) / len(word), 4)] for i in set(word)}
    # print(dict_count_frequency)

    tree = Tree(dict_count, word)
    tree.get_code()
    print(tree.char_coded)
    compression_ratio = 0
    print(tree.encrypt())
    a = tree.encrypt()
    print(Tree.decrypt(a, tree.char_coded))

    for i in tree.char_coded:
        compression_ratio += len(tree.char_coded[i]) * dict_count[i]
    print(math.ceil(compression_ratio/8))
    k = round(len(word) / math.ceil(compression_ratio / 8), 2)
    print(k)



if __name__ == '__main__':
    main()

